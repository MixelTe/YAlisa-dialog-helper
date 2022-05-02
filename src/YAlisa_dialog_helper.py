from typing import Literal, Tuple, Union
import logging
import traceback

class DialogBase:
    """Класс для создания диалогов для Яндекс Алисы

    Унаследованный класс должен содержать функцию start, которая будет вызываться в начале диалога.

    Функция должна возвращать кортеж из:
    * ответ пользователю (str)
    * следующая часть диалога (функция) или False (если конец диалога)

    Чтобы сохранить данные между частями диалога, используйте:
    - self["поле"] = значение
    - a = self["поле"]

    Чтобы передать параметры для следующей функции части диалога:
    - self.args = список параметров

    Чтобы предварительно установить данные, назначьте словарь статическому полю data:
        class MyDialog(DialogBase):
            data = {"поле": "значение"}

    Внутри функции вы можете получить:
    * self.text - Команда пользователя
    * self.textOrig - оригинальное произнесение команды
    * self.tokens - слова в команде
    ---
    * self.people - список людей в запросе
    * self.airports - список аэропортов в запросе
    * self.cities - список городов в запросе
    * self.countries - список стран в запросе
    * self.house_numbers - список номеров домов в запросе
    * self.streets - список улиц в запросе
    ---
    * self.FIO - первый FIO в списке или ("", "", "")
    * self.airport - первый аэропорт в списке или None
    * self.city - первый город в списке или None
    * self.country - первая страна в списке или None
    * self.house_number - первый номер дома в списке или None
    * self.street - первая улица в списке или None

    Добавить в ответ:
    * self.tts: str - строка для преобразования текста в речь
    * self.addButton() - добавить кнопку
    * self.addButtons() - добавить несколько кнопок
    * self.setCard_BigImage() - установить карточку BigImage в ответ
    * self.setCard_ItemsList() - установить карточку ItemsList в ответ
    * self.setCard_ImageGallery() - установить карточку ImageGallery в ответ
    """
    def __init__(self, req, data):
        self.req: dict = req
        self.res: dict = {}
        self._data: dict = data["data"]
        self.args = data["args"]
        self._fun = getattr(self, str(data["fun"]))

        self.airports, self.airport = self._getGEO("airport")
        self.cities, self.city = self._getGEO("city")
        self.countries, self.country = self._getGEO("country")
        self.house_numbers, self.house_number = self._getGEO("house_number")
        self.streets, self.street = self._getGEO("street")
        self.people, self.FIO = self._getFIO()

        self.text = req["request"]["command"]
        self.tts: str = None
        self.textOrig = req["request"]["original_utterance"]
        self.tokens = req["request"]["nlu"]["tokens"]

    def __getitem__(self, *args):
        return self._data.__getitem__(*args)

    def __setitem__(self, *args):
        self._data.__setitem__(*args)

    def __delitem__(self, *args):
        self._data.__delitem__(*args)

    def _getGEO(self, type: Union[Literal["country"], Literal["city"], Literal["street"], Literal["house_number"], Literal["airport"]]) -> Tuple[list[str], Union[str, None]]:
        items = []
        firstItem = None
        for entity in self.req['request']['nlu']['entities']:
            if entity['type'] == 'YANDEX.GEO':
                if (type in entity['value']):
                    items.append(entity['value'][type])
        if (len(items) > 0):
            firstItem = items[0]
        return items, firstItem

    def _getFIO(self) -> Tuple[list[Tuple[str, str, str]], Tuple[str, str, str]]:
        items = []
        firstItem = ("", "", "")
        for entity in self.req['request']['nlu']['entities']:
            if entity['type'] == 'YANDEX.FIO':
                first_name = entity['value'].get("first_name", "")
                patronymic_name = entity['value'].get("patronymic_name", "")
                last_name = entity['value'].get("last_name", "")
                items.append((first_name, patronymic_name, last_name))
        if (len(items) > 0):
            firstItem = items[0]
        return items, firstItem

    @staticmethod
    def _createNewData(cls):
        return {
            "data": cls.data,
            "fun": "start",
            "args": [],
        }

    def _run(self):
        res = self._fun(*self.args)
        if (isinstance(res, tuple)):
            text, next = res
        else:
            text, next = res, False
        if (callable(next)):
            self._fun = next.__name__
        self.res["text"] = str(text)
        if (self.tts):
            self.res["tts"] = str(self.tts)
        self.res["end_session"] = next == False

    def addButton(self, title, hide=True, url=None, payload=None):
        """Добавить кнопку в ответ"""
        if ("buttons" not in self.res):
            self.res["buttons"] = []
        button = {
            "title": title,
            "hide": hide
        }
        if (url):
            button["url"] = url
        if (payload):
            button["payload"] = url
        self.res["buttons"].append(button)

    def addButtons(self, buttons: list[Union[str, tuple[str, bool], tuple[str, bool, str]]]):
        """Добавить кнопки в ответ
        :param buttons: список кортежей(title, hide, url) или кортежей(title, hide) или str
        """
        for btn in buttons:
            if (isinstance(btn, tuple)):
                self.addButton(*btn)
            else:
                self.addButton(str(btn))

    def setCard_BigImage(self, title: str, imgId: str, descripton="", button=None):
        """Установить карточку BigImage в ответ
        :param button: словарь с полями: text, url, payload
        https://yandex.ru/dev/dialogs/alice/doc/response-card-bigimage.html#response-card-bigimage__card-button-desc
        """
        card = {
            "type": "BigImage",
            "image_id": imgId,
            "title": title,
        }
        if (descripton):
            card["descripton"] = descripton
        if (button):
            card["button"] = button
        self.res["card"] = card

    def setCard_ItemsList(self, items: list[dict], header: str = None, footer: dict = None):
        """Установить карточку ItemsList в ответ
        :param items: список словарей https://yandex.ru/dev/dialogs/alice/doc/response-card-itemslist.html#response-card-itemslist__items-desc

        :param footer: словарь с полями: text, button https://yandex.ru/dev/dialogs/alice/doc/response-card-itemslist.html#response-card-itemslist__footer-desc
        """
        card = {
            "type": "ItemsList",
            "items": items
        }
        if (header):
            card["header"] = {"text": header}
        if (footer):
            card["footer"] = footer
        self.res["card"] = card

    def setCard_ImageGallery(self, items: list[dict]):
        """Установить карточку ImageGallery в ответ
        :param items: список словарей https://yandex.ru/dev/dialogs/alice/doc/response-card-imagegallery.html#response-card-imagegallery__items-desc
        """
        card = {
            "type": "ImageGallery",
            "items": items
        }
        self.res["card"] = card


class DialogManager:
    def __init__(self, dialog: type[DialogBase]):
        self.sessionStorage = {}
        self.dialog = dialog

    def handle_dialog(self, req):
        response = {
            'session': req['session'],
            'version': req['version'],
            'response': {},
        }
        user_id = req['session']['user_id']
        if (req['session']['new'] or user_id not in self.sessionStorage):
            self.sessionStorage[user_id] = DialogBase._createNewData(self.dialog)
        data = self.sessionStorage[user_id]
        dialog = self.dialog(req, data)
        try:
            dialog._run()
            data["fun"] = dialog._fun
            data["args"] = dialog.args
            data["data"] = dialog._data
            response['response'] = dialog.res
        except Exception as x:
            logging.error(f"{x}\n{traceback.format_exc()}")
            response['response'] = {
                "text": "Что-то пошло не так :(",
                "end_session": True,
            }
        if (response["response"]["end_session"]):
            del self.sessionStorage[user_id]
        return response
