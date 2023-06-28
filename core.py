from datetime import datetime 
import vk_api

from config import access_token

class VkTools():
    def __init__(self, access_token):
       self.api = vk_api.VkApi(token=access_token)

    def get_profile_info(self, user_id):

        info, = self.api.method('users.get',
                            {'user_id': user_id,
                            'fields': 'city,bdate,sex,relation,home_town,city' 
                            }
                            )
        bdate = info['bdate'] if 'bdate' in info else None
        if bdate:
            current_year = datetime.now().year
            user_year = int(info['bdate'].split('.')[2])
            age = current_year - user_year
        user_info = {'name': info['first_name'] + ' '+ info['last_name'],
                     'id':  info['id'],
                     'age': age if 'bdate' in info else None,
                     'hometown': info['city']['title'] if 'city' in info else None,
                     'sex': info['sex'] if 'sex' in info else None,
                     }
        return user_info
    
    def search_users(self, params):
        hometown = params['hometown']
        age = params['age']
        sex = 1 if params['sex'] == 2 else 2
        age_from = age - 3
        age_to = age + 3

        users = self.api.method('users.search',
                                {'count': 100,
                                 'offset': 0,
                                 'age_from': age_from,
                                 'age_to': age_to,
                                 'sex': sex,
                                 'hometown': hometown,
                                 'status': 6,
                                 'is_closed': False
                                }
                            )
        try:
            users = users['items']
        except KeyError:
            return []
        
        res = []

        for user in users:
            if user['is_closed'] == False: #and user['id'] ==  27315722: 
                res.append({'id' : user['id'],
                            'name': user['first_name'] + ' ' + user['last_name']
                           }
                           )
        return res

    def get_photos(self, user_id):
        photos = self.api.method('photos.get',
                                 {'user_id': user_id,
                                  'album_id': 'profile',
                                  'extended': 1
                                 }
                                )
        try:
            photos = photos['items']
        except KeyError:
            return []
        
        res = []

        for photo in photos:
            res.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        }
                        )
            
        res.sort(key=lambda x: x['likes']+x['comments']*10, reverse=True)

        return res


if __name__ == '__main__':
    bot = VkTools(access_token)
    user_id = 17505384
    params = bot.get_profile_info(user_id)
    print(params)
    #print(bot.get_photos(users[2]['id']))
    #users = bot.search_users(params)
    #print(params)
