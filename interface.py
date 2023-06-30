# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import community_token, access_token
from core import VkTools

from data_store import db

def check_data(data_type, data):
    if not data:
        return False
    elif data_type == 'age':
        if not data.isnumeric():
            return False
        return (15 < int(data) < 100)
    elif data_type == 'sex':
        return data.lower() in 'мж'
    elif data_type == 'hometown':
        return data.isalpha()
    else:
        return False


class BotInterface():

    def __init__(self,comunity_token, access_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(access_token)
        self.params = None


    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                                {'user_id': user_id,
                                'message': message,
                                'attachment': attachment,
                                'random_id': get_random_id()
                                }
                                )
        
    def event_handler(self):
        longpoll = VkLongPoll(self.interface)
        users = []
        i = 0

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'здравствуй {self.params["name"]}')
                    #del self.params['age']
                    if not 'age' in self.params:
                        age = None
                        while not check_data('age',age):
                            self.message_send(event.user_id,
                                            f' Дата рождения не найдена в профиле или задана не верно. Ведите возраст (число от 16 до 99)',
                                            )   
                            for event in longpoll.listen():
                                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                    age = event.text
                                    break
                        self.params['age'] = age
                        self.message_send(event.user_id,
                            f'Принято',
                            ) 
                    #del self.params['sex']
                    if not 'sex' in self.params:
                        sex = None
                        while not check_data('sex',sex):
                            self.message_send(event.user_id,
                                        f'Пол не указан в профиле. Ведите М или Ж',
                                        )
                            for event in longpoll.listen():
                                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                    sex = event.text
                                    break
                        self.params['sex'] = 1 if sex.lower() == 'ж' else 2;  
                        self.message_send(event.user_id,
                            f'Принято',
                            ) 
                        
                    #del self.params['hometown']
                    if not 'hometown' in self.params:
                        self.message_send(event.user_id,
                                    f'Город не указан в профиле. Введите город',
                                    )
                        for event in longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                self.params['hometown'] = event.text.capitalize()   
                                self.message_send(event.user_id,
                                    f'Ваш город - {self.params["hometown"]}',
                                    ) 
                                break
                elif command == 'поиск':
                    if not self.params:
                        self.message_send(event.user_id,
                            f'Сначала авторизуйтесь, написав "Привет"',
                            )   
                    else:
                        if len(users) < 1:
                            users = self.api.search_users(self.params,i*10)
                            if len(users) < 1:
                                self.message_send(event.user_id,
                                f'Для Вас никого не найдено',
                                )   
                            i += 1    
                        if len(users) > 0:
                            user = users.pop()
                            #логика для проверки бд
                            while db.check_user(event.user_id,user['id']):
                                if len(users) > 0:
                                    user = users.pop()
                            if len(users) > 0: 
                                photos_user = self.api.get_photos(user['id'])                  
                                
                                attachment = ''
                                for num, photo in enumerate(photos_user):
                                    attachment += f',photo{photo["owner_id"]}_{photo["id"]}'
                                    if num == 2:
                                        break
                                self.message_send(event.user_id,
                                                f' {user["name"]} vk.com/id{user["id"]}',
                                                attachment=attachment
                                                )
                                #здесь логика для добавленяи в бд
                                db.add_user(event.user_id,user['id']) 
                            else:
                                self.message_send(event.user_id,
                                f'Закончились загруженные анкеты, выполните поиск ещё раз',
                                )    
                elif command == 'пока':
                    self.message_send(event.user_id, 'пока')
                else:
                    self.message_send(event.user_id, 'команда не опознана')



if __name__ == '__main__':
    bot = BotInterface(community_token, access_token)
    bot.event_handler()