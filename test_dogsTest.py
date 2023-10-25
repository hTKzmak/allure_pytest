import pytest
import requests
import allure

import pprint
from pydantic import BaseModel, ValidationError
from typing import Dict, List

class paramDog(BaseModel):
    dog: str
    status: str

class DogBreeds(BaseModel):
    message: Dict[str, List[str]]
    status: str
class BaseRequest:
    def __init__(self, base_url):
        self.base_url = base_url
        # set headers, authorisation etc

    def _request(self, url, request_type, data=None, expected_error=False):
        stop_flag = False
        while not stop_flag:
            if request_type == 'GET':
                response = requests.get(url)
            elif request_type == 'POST':
                response = requests.post(url, data=data)
            else:
                response = requests.delete(url)

            if not expected_error and response.status_code == 200:
                stop_flag = True
            elif expected_error:
                stop_flag = True

        # log part
        pprint.pprint(f'{request_type} example')
        pprint.pprint(response.url)
        pprint.pprint(response.status_code)
        pprint.pprint(response.reason)
        pprint.pprint(response.text)
        pprint.pprint(response.json())
        pprint.pprint('**********')
        return response

    def get(self, endpoint, endpoint_id, expected_error=False):
        url = f'{self.base_url}/{endpoint}/{endpoint_id}'
        response = self._request(url, 'GET', expected_error=expected_error)
        return response.json()

    def post(self, endpoint, endpoint_id, body):
        url = f'{self.base_url}/{endpoint}/{endpoint_id}'
        response = self._request(url, 'POST', data=body)
        return response.json()['message']

    def delete(self, endpoint, endpoint_id):
        url = f'{self.base_url}/{endpoint}/{endpoint_id}'
        response = self._request(url, 'DELETE')
        return response.json()['message']


BASE_URL_DOGS = 'https://dog.ceo/api/breeds/list/all'
base_request = BaseRequest(BASE_URL_DOGS)



# 1 Проверка статуса у 3-х собак +

@allure.feature('Dogs status')
@allure.story('Проверка статуса у 3-х собак')
@pytest.mark.parametrize('breed', ['affenpinscher', 'african', 'akita'])
def test_dog_breeds(breed):
    with allure.step('Отправка GET-запроса'):
        response = requests.get(f'{BASE_URL_DOGS}')
    with allure.step('Подтвердить ответ'):
        assert response.status_code == 200
        try:
            data = DogBreeds.model_validate_json(response.text)
            assert data.status == 'success'
            assert breed in data.message.keys()
        except ValidationError as e:
            assert False, f'Validation error: {e}'


# 2 Проверка на то, действительно ли в данной ссылке (https://dog.ceo/api/breed/hound/afghan/images/random/3) около 3-х ссылок на изображение +
dogs_message_value = requests.get('https://dog.ceo/api/breed/hound/afghan/images/random/3')
pprint.pprint(dogs_message_value)

@allure.feature('3 Links of image')
@allure.story('Проверка на то, действительно ли в данной ссылке около 3-х ссылок на изображение')
def test_value():
    with allure.step('Проверка количества ссылок'):
        assert 3 == len(dogs_message_value.json()['message'])


# 3 проверка статуса у определённой пароды собак в json файле (по ссылке) +
own_dog_success = requests.get('https://dog.ceo/api/breed/hound/list')
pprint.pprint(own_dog_success)

@allure.feature('Status of choosen dogs')
@allure.story('проверка статуса у определённой пароды собак в json файле')
@pytest.mark.parametrize('param', ['afghan', 'blood', 'plott', 'walker'])
def test_dog(param):
    with allure.step('Проверка статуса если данная порода имеется в списке'):
        if param in own_dog_success.json()['message']:
            assert own_dog_success.json()['status'] == 'success'
        else:
            assert False


# 4 Проверка на то, есть ли изображение с указанным названием файла и пса
@allure.feature('Availability of image')
@allure.story('Проверка на то, есть ли изображение с указанным названием файла и пса')
@pytest.mark.parametrize('mainName, secName, image', [('hound', 'hound-basset', 'n02088238_10102.jpg'), ('mexicanhairless', 'mexicanhairless', 'n02113978_304.jpg')])
def test_name_image(mainName, secName, image):
    with allure.step('Получение ссылок'):
        response = requests.get(f'https://dog.ceo/api/breed/{mainName}/images')
        link = f'https://images.dog.ceo/breeds/{secName}/{image}'
    with allure.step('Проверка наличия изображения'):
        assert link in response.json()['message']

# 5 Получение полного списка определённой собаки +
@allure.feature('Full list of dog')
@allure.story('Получение полного списка определённой собаки')
@pytest.mark.parametrize('name', ['breeds'])
def test_get_all_breeds(name):
    with allure.step('Получение ссылки'):
        response = requests.get(f'https://dog.ceo/api/{name}/list/all')
    with allure.step('Проверка статуса и длины json файла'):
        assert response.status_code == 200
        assert len(response.json()["message"]) > 0
    with allure.step('Вывод списка'):
        print(f"Список породы {name}: {response.json()['message']}")


# BASE_URL_DOGS = 'https://dog.ceo/api/breeds/list/all'





