import requests
import pytest
import pprint
import json
import allure
from pydantic import BaseModel

class UserInfoModel(BaseModel):
    id: int
    name: str
    username: str
    email: str

class OrderModel(BaseModel):
    id: int
    petId: int
    quantity: int
    shipDate: str
    status: str
    complete: bool

class PetModel(BaseModel):
    id: int
    name: str

class BaseRequest:
    def __init__(self, base_url):
        self.base_url = base_url

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


BASE_URL = 'https://jsonplaceholder.typicode.com'

base_request = BaseRequest(BASE_URL)

def test_get_user_info():
    with allure.step('Get user info'):
        user_info = base_request.get('users', 1)
        expected_info = UserInfoModel(**user_info)
        assert expected_info == UserInfoModel(id=1, name='Leanne Graham', username='Bret', email='Sincere@april.biz')


def test_create_user():
    with allure.step('Create a new user'):
        data = {
            'name': 'John Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com'
        }
        new_user = base_request.post('users', 1, data)
        expected_message = "New user added"
        assert new_user == expected_message


inventory = base_request.get('store', 'inventory')
pprint.pprint(inventory)

data = {
'id': 1,
'petId': 1,
'quantity': 1,
'shipDate': '2023-10-07T10:00:00.000Z',
'status': 'placed',
'complete': False
}
new_order = base_request.post('store', 'order', data=data)
pprint.pprint(new_order)

order_info = base_request.get('store', 'order/1')
pprint.pprint(order_info)

deleted_order = base_request.delete('store', 'order/1')
pprint.pprint(deleted_order)


data = {'name': 'NewName'}
pet_id = base_request.put('pet', 1, data)
pet_info = base_request.get('pet', pet_id)
assert data['name'] == pet_info['name']

def test_update_pet_info():
    with allure.step('Update pet info'):
        data = {'name': 'NewName'}
        pet_id = base_request.put('pet', 1, data)
        pet_info = base_request.get('pet', pet_id)
        expected_pet_info = PetModel(**pet_info)
        expected_data = PetModel(id=1, name='NewName')
        assert expected_pet_info == expected_data


@pytest.fixture
def allure_dynamic():
    with allure.step('Dynamically add a new step'):
        pass


# # получение пользователя
# user_info = base_request.get('users', 1)
# pprint.pprint(user_info)
#
# # создание нового пользователя
# data = {
#     'name': 'John Doe',
#     'username': 'johndoe',
#     'email': 'johndoe@example.com'
# }
# new_user = base_request.post('users', 1, data)
# pprint.pprint(new_user)
#
# # обновление пользователя
# data = {
#     'name': 'Jane Doe',
#     'username': 'janedoe',
#     'email': 'janedoe@example.com'
# }
# updated_user = base_request.post('users', 1, data=data)
# pprint.pprint(updated_user)
#
# # удаление пользователя
# deleted_user = base_request.delete('users', 1)
# pprint.pprint(deleted_user)
#
#
#
# BASE_URL = 'https://petstore.swagger.io/v2'
# base_request = BaseRequest(BASE_URL)
#
# # получение магазина
# inventory = base_request.get('store', 'inventory')
# pprint.pprint(inventory)
#
# # размещение заказ в магазине
# data = {
#     'id': 1,
#     'petId': 1,
#     'quantity': 1,
#     'shipDate': '2023-10-07T10:00:00.000Z',
#     'status': 'placed',
#     'complete': False
# }
# new_order = base_request.post('store', 'order', data=data)
# pprint.pprint(new_order)
#
# # получение заказа
# order_info = base_request.get('store', 'order/1')
# pprint.pprint(order_info)
#
# # удаление заказа
# deleted_order = base_request.delete('store', 'order/1')
# pprint.pprint(deleted_order)