# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import community_token, access_token
from core import VkTools

from data_store import db

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

        waiting_command = False
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and not waiting_command:
                command = event.text.lower()

                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'здравствуй {self.params["name"]}')

                    if not 'age' in self.params:
                        self.message_send(event.user_id,
                                    f' Дата рождения не найдена в профиле. Ведите дату рождения',
                                    )   
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            self.params['age'] = event.text
                    if not 'sex' in self.params:
                        self.message_send(event.user_id,
                                    f'Пол не указан в профиле. Ведите М или Ж',
                                    )
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            self.params['sex'] = 1 if event.text.lower() == 'Ж' else 2;  
                    if not 'hometown' in self.params:
                        self.message_send(event.user_id,
                                    f'Город не указан в профиле. Введите город',
                                    )
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            self.params['hometown'] = event.text    
                elif command == 'поиск':
                    users = self.api.search_users(self.params)
                    #здесь логика дял проверки бд
                    user = users.pop()
                    while db.check_user(event.user_id,user['id']):
                       user = users.pop() 
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
                    db.add_user(event.user_id,user['id']) 
                    #здесь логика для добавленяи в бд
                elif command == 'пока':
                    self.message_send(event.user_id, 'пока')
                else:
                    self.message_send(event.user_id, 'команда не опознана')



if __name__ == '__main__':
    bot = BotInterface(community_token, access_token)
    bot.event_handler()

            

