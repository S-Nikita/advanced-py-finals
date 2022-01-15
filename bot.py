from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll

class Bot:

    def __init__(self, community_token, profile_dict = {}):
        self.token = community_token
        self.profile_dict = profile_dict
        
    def longpoll_listen(self):
        self.vk = vk_api.VkApi(token=self.token)
        longpoll = VkLongPoll(self.vk)

        return longpoll
    
    # Метод отправки обычных сообщений
    def write_msg(self, user_id, message):
        self.vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})

    # Метод отправки сообщений с вложением
    def write_extended_msg(self, user_id):
        self.vk = vk_api.VkApi(token=self.token)
        i = 0
        # Для каждого найденного профиля получаем информацию о самых популярных его фотографиях, а также ссылку на аккаунт и имя
        for k, v in self.profile_dict.items():
            if i < len(self.profile_dict) / 2:
                user_name = self.profile_dict[f"user_name{i}"]
            attachment_str = ''
            if 'user_name' not in k:
                for photo in v:
                    photo_id = photo
                    owner_id = k.replace('https://vk.com/id', '')
                    attachment_str += f"photo{owner_id}_{photo_id},"

                self.vk.method('messages.send', {'user_id': user_id, 'message': f"{user_name}: {k}",  'random_id': randrange(10 ** 7), 'attachment': attachment_str})
                i += 1
        



