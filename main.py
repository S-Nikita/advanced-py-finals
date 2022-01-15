from time import sleep
from unicodedata import name
import vk_info
import bot
from vk_api.longpoll import VkEventType

if __name__ == '__main__':
    community_token = ''
    user_token = ''
    preferences_dict = {}
    user = vk_info.Vk_users(user_token, preferences_dict)
    user_id = user.get_main_user_info()['id']
    user_name = user.get_main_user_info()['first_name']
    
    age_from = None
    bot_simple = bot.Bot(community_token)
    for event in bot_simple.longpoll_listen().listen():
        if event.type == VkEventType.MESSAGE_NEW:

            if event.to_me:
                request = event.text
                # Не успел разобраться с тем, как сделать бота интеррактивным, чтобы он ожидал input от пользователя
                # поэтому в этой секции огромные костыли с кучей условностей, чтобы имитировать взаимодействие с нимЫ
                if request.lower() == "hi":
                    bot_simple.write_msg(event.user_id, f"Hi, {user_name}! To continue using the service you'll be asked to specify some information about people you are looking for.")
                    bot_simple.write_msg(event.user_id, 'Do you wish to continue? (yes/no)')
                elif request == "yes":
                    bot_simple.write_msg(event.user_id, "Excelent! Let's start!")
                    bot_simple.write_msg(event.user_id, "1) Choose the gender of the person you're looking for (F/M)")
                elif request.lower() in ['f', 'm']:
                    if request.lower() == 'f':
                        gender = 1
                    elif request.lower() == 'm':
                        gender = 2
                    else:
                        gender = 0
                    preferences_dict['gender'] = gender
                    bot_simple.write_msg(event.user_id, "2) Choose the city of the person you're looking for")
                elif request.isalpha() and request.lower() not in ['yes', 'no']:
                    city = request
                    preferences_dict['city'] = city
                    bot_simple.write_msg(event.user_id, "3) Choose minimal age of the person you're looking for")
                elif request.isdigit() and age_from is None:
                    age_from = int(request)
                    preferences_dict['age_from'] = age_from
                    bot_simple.write_msg(event.user_id, "4) Choose maximum age of the person you're looking for")
                elif request.isdigit() and age_from is not None:
                    age_to = int(request)
                    preferences_dict['age_to'] = age_to
                    break
                else:
                    bot_simple.write_msg(event.user_id, "Don't recognize your input")
                    break
    # После сбора необходимой информации по поиску людей вызываются методы по потбору людей, подходящих под заданные условия
    info = vk_info.Vk_users(user_token, preferences_dict)
    result = info.get_photos()
    # Возвращение ответа с информацией о найденных людях пользователю с вложенными фотографиями
    extended_bot = bot.Bot(community_token, result)
    bot_simple.write_msg(event.user_id, "Here are some people you might be interested in:")
    extended_bot.write_extended_msg(event.user_id)

