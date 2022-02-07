import imp
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from settings import DATABASES

# Определение engine подключения
def get_engine(engine, user, password, host, port, db):
    url = f"{engine}://{user}:{password}@{host}:{port}/{db}"
    if not(database_exists(url)):
        create_database(url)  
    engine = create_engine(url)

    return engine

# Получение конфигурации подключения к БД
def get_connection_params(connection_settings):
    keys = ['engine', 'user', 'password', 'host', 'port', 'db']
    if not all(key in keys for key in connection_settings['postgresql'].keys()):
        raise Exception('Invalid config file')

    return get_engine(
                        connection_settings['postgresql']['engine'],
                        connection_settings['postgresql']['user'],
                        connection_settings['postgresql']['password'],
                        connection_settings['postgresql']['host'],
                        connection_settings['postgresql']['port'],
                        connection_settings['postgresql']['db']
                    )

# Создание соединения с БД и проверка на наличие нужной таблицы
def get_connection():
    engine = get_connection_params(DATABASES)
    connection = engine.connect()

    connection.execute(
        """CREATE TABLE IF NOT EXISTS users (
                id INT GENERATED ALWAYS AS IDENTITY,
                user_id varchar(50) NOT NULL,
                user_name varchar(50) NOT NULL,
                user_url varchar(100) NOT NULL
            );
        """
    )

# Запись основной информации о пользователях в таблицу
def insert_to_db(user_info):
    engine = get_connection_params(DATABASES)
    connection = engine.connect()
    print(user_info)
    print(len(user_info.keys()))
    i = 0
    for k in user_info.keys():
        if i < len(user_info.keys()) / 2:
            user_name = user_info[f"user_name{i}"]
            print(user_name)
        if 'user_name' not in k:
            user_id = str(k.replace('https://vk.com/id', ''))
            user_url = 'https://vk.com/id' + user_id
            print(user_id, user_name, user_url)
            connection.execute(
                f"""
                    INSERT INTO users(user_id, user_name, user_url) VALUES('{user_id}', '{user_name}', '{user_url}')
                """
            )
        i += 1

get_connection()


