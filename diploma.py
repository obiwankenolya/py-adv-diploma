from pprint import pprint
from urllib.parse import urlencode
from pymongo import MongoClient
from unittest.mock import patch
import requests
import json
import time
import unittest


APP_ID = 7060537

client = MongoClient()
obiwankenolya_db = client['obiwankenolya']

BASE_URL = 'https://oauth.vk.com/authorize'
auth_data = {
    'client_id': APP_ID,
    'response_type': 'token',
    'v': '5.101'
}
# print('?'.join((BASE_URL, urlencode(auth_data))))

TOKEN = 'cd8a45537d43c1b3f7fab84a66e8411cf935d724d331dd8fd958005e8a2802e0e24bf68e7c49396acf3d8'


class User:
    def __init__(self, token):
        self.token = token

    def get_params(self):
        params = dict(
            access_token=self.token,
            v='5.101',
            count=1000,
            has_photo=1,
            status=6,
            fields='interests, movies, music, books, games'
        )
        id_input = input('Введите свой id или username: ')
        if type(id_input) == int:
            params['user_id'] = {id_input}
        else:
            params['screen_name'] = {id_input}
        print('Доступные параметры поиска: sex (пол), age_from (минимальный возраст), age_to (максимальный'
              'возраст), hometown (город), religion (религия), position (должность/профессия).')
        s_params_input = input('Введите параметры поиска: ')
        search_params = list(s_params_input.split(','))
        for search_param in search_params:
            if 'sex' in search_param:
                sex_input = input('Введите пол партнера по коду: женщина - 1, мужчина - 2, не важно - 0 ')
                params['sex'] = sex_input
            if 'age_from' in search_param:
                age_from_input = input('Введите минимальный возраст партнера: ')
                params['age_from'] = age_from_input
            if 'age_to' in search_param:
                age_to_input = input('Введите максимальный возраст партнера: ')
                params['age_to'] = age_to_input
            if 'hometown' in search_param:
                hometown_input = input('Введите название города: ')
                params['hometown'] = hometown_input
            if 'religion' in search_param:
                religion_input = input('Введите религию партнера: ')
                params['religion'] = religion_input
            if 'position' in search_param:
                position_input = input('Введите должность партнера: ')
                params['position'] = position_input
        return params

    def get_partners(self):
        params = self.get_params()
        final_list = []
        response = requests.get(
            'https://api.vk.com/method/users.search',
            params
        )
        resp_json = response.json()['response']['items']
        if 'error' in resp_json and 'error_code' in resp_json['error'] and resp_json['error']['error_code'] == 6:
            time.sleep(2)
        counter = 0
        with open('previous-results.txt', 'r+') as f:
            previous_results = f.read()
            for person in resp_json:
                id = str(person['id'])
                if counter < 10 and id not in previous_results:
                    final_list.append(person)
                    f.write(f' {id} ')
                    counter += 1
                else:
                    continue
        return final_list
        # pprint(final_list)

    def add_top3_photos(self):
        final_list = list(self.get_partners())
        params = dict(
            access_token=self.token,
            v='5.101',
            album_id='profile',
            extended=1
        )
        for person in final_list:
            params['owner_id'] = person['id']
            response = requests.get(
                'https://api.vk.com/method/photos.get',
                params
            )
            resp_json = response.json()['response']['items']
            if 'error' in resp_json and 'error_code' in resp_json['error'] and resp_json['error']['error_code'] == 6:
                time.sleep(1)
            top_dict = {'1': {'link': 0, 'likes_amount': 0},
                        '2': {'link': 0, 'likes_amount': 0},
                        '3': {'link': 0, 'likes_amount': 0}}
            for photo in resp_json:
                if 'error' in resp_json and 'error_code' in resp_json['error'] and \
                        resp_json['error']['error_code'] == 6:
                    time.sleep(1)
                likes_amount = int(photo['likes']['count'])
                i = len(photo['sizes'])
                if likes_amount >= top_dict['1']['likes_amount']:
                    top_dict['1'] = {'link': photo['sizes'][i-1]['url'], 'likes_amount': likes_amount}
                elif likes_amount >= top_dict['2']['likes_amount']:
                    top_dict['2'] = {'link': photo['sizes'][i-1]['url'], 'likes_amount': likes_amount}
                elif likes_amount >= top_dict['3']['likes_amount']:
                    top_dict['3'] = {'link': photo['sizes'][i-1]['url'], 'likes_amount': likes_amount}
            person['top3_photos'] = top_dict
        with open('vkinder.json', 'w') as file:
            json.dump(final_list, file, ensure_ascii=False, indent=2)

    def add_to_bd(self, db):
        partners_collection = db['partners']
        with open('vkinder.json') as file:
            vkinder_json = json.load(file)
        for person in vkinder_json:
            partner = {
                'id': person['id'],
                'first_name': person['first_name'],
                'last_name': person['last_name'],
                'top3_photos': person['top3_photos']
            }
            db.partners_collection.insert_one(partner)
        return partners_collection


user1 = User(TOKEN)

if __name__ == '__main__':
    user1.add_top3_photos()
