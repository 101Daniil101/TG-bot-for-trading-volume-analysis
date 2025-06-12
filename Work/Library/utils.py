import requests


def send_request(url_full: str, method: str, params: dict, headers: dict,
                 **kwargs):
    # Отправляет HTTP-запрос по указанному URL с заданным методом и параметрами
    try:
        # Проверяет, является ли метод POST
        if method.upper() == "POST":
            response = requests.request(method, url_full, headers=headers,
                                       data=params)
        # Проверяет, является ли метод GET
        elif method.upper() == "GET":
            response = requests.request(method, url_full, headers=headers,
                                       params=params)
        # Проверяет статус ответа на наличие HTTP-ошибок
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Выводит сообщение об ошибке сети в консоль
        print(f"[Ошибка сети] {e}")
        # Возвращает словарь с информацией об ошибке
        return {"error": "network", "message": str(e)}
    # Возвращает JSON-ответ от сервера
    return response.json()
