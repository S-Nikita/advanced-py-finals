import sys
import requests
from db import insert_to_db
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

get_token = 'https://oauth.vk.com/authorize?client_id=8047535&display=page&response_type=token&v=5.131'

class Vk_users():
    base_url = 'https://api.vk.com/method/'

    def __init__(self, token, preferences_dict):
        self.token = token
        self.preferences_dict = preferences_dict

    # Получение информации о пользователе, взаимодействующем с ботом
    def get_main_user_info(self):
        result = {}
        method = 'users.get'
        url = self.base_url + method
        params = {
            "v": '5.131',
            "access_token": self.token
        }

        res = requests.get(url=url, params=params)
        res.raise_for_status()

        result['id'] = res.json()['response'][0]['id']
        result['first_name'] = res.json()['response'][0]['first_name']

        return result


    # Получение ID города по его названию для дальнейшего поиска людей в указанном регионе
    def _get_city_id(self):
        method = 'database.getCities'
        url = self.base_url + method
        # city = input(
        #     'Введите название желаемого города для поиска людей: ')
        city = self.preferences_dict['city']
        params = {
            "v": '5.131',
            "access_token": self.token,
            "country_id": 1,
            "q": city,
            "count": 1
        }
        res = requests.get(url=url, params=params)
        res.raise_for_status()

        return res.json()['response']['items'][0]['id']

    # Получение профилей людей, подходящих по условию поиска
    def _get_user_info(self):
        method = 'users.search'
        url = self.base_url + method
        city_id = self._get_city_id()
        min_age = self.preferences_dict['age_from']
        max_age = self.preferences_dict['age_to']
        gender = self.preferences_dict['gender']
        params = {
            "v": '5.131',
            "access_token": self.token,
            "fields": 'relation',
            "age_from": min_age,
            "age_to": max_age,
            "has_photo": 1,
            "sex": gender,
            "status": 6,
            "is_closed": False,
            "city": city_id,
            "count": 5
        }
        res = requests.get(url=url, params=params)
        res.raise_for_status()

        return res.json()

    # Получение самых популярных фотографий и формирование справочника с нужной информацией для отправки пользователю
    def get_photos(self):
        users_list = self._get_user_info()['response']['items']
        method = 'photos.get'
        album_id = 'profile'
        url = self.base_url + method
        user_base_url = 'https://vk.com/id'
        user_dict = {}
        i = 0
        for user in users_list:
            # По каким-то причинам VK подсовывает закрытые аккаунты, даже если в параметрах запроса указано is_closed: False
            if user['is_closed'] == False:
                photo_ids_list = []
                user_id = user['id']
                user_name = f"{user['first_name']} {user['last_name']}"
                user_url = user_base_url + str(user_id)
                params = {
                    "v": '5.131',
                    "access_token": self.token,
                    "owner_id": user_id,
                    "album_id": album_id,
                    "extended": 1,
                    "photo_sizes": 0
                }

                res = requests.get(url=url, params=params)
                res.raise_for_status()
                result = res.json()['response']['items']
                
                likes = [photo_info['likes']['count'] for photo_info in result]
                comments = [photo_info['comments']['count']
                            for photo_info in result]
                photo_ids = [photo_info['id']
                            for photo_info in result]
                popular = sorted(zip(likes, comments, photo_ids), reverse=True)[:3]

                for photo in popular:
                    photo_ids_list.append(photo[2])

                user_dict[user_url] = photo_ids_list
                user_dict[f"user_name{i}"] = user_name
                i += 1
        insert_to_db(user_dict)
        return user_dict
