# Упрощение создания диалогов с Яндекс Алисой

Всё необходимое в файле [YAlisa_dialog_helper.py](https://github.com/MixelTe/YAlisa-dialog-helper/blob/master/YAlisa_dialog_helper.py)

# Использование
На старте необходимо создать DialogManager и при запросе вызывать у экземпляра метод handle_dialog.
Метод handle_dialog принимает распарсенный json запроса и возвращает ответ в виде словаря.

```py
from YAlisa_dialog_helper import DialogManager
dialogManager = DialogManager(Dialog)  # Dialog - см. ниже

def AlicePost():
    response = dialogManager.handle_dialog(request.json)
```

## Диалог
Класс диалога должен быть уналедован от DialogBase.

Унаследованный класс должен содержать функцию start, которая будет вызываться в начале диалога.

Каждая функция диалога должна возвращать кортеж из:
* ответ пользователю (str)
* следующая часть диалога (функция) или False (если конец диалога)

Чтобы сохранять данные между частями диалога, используйте:
- self["поле"] = значение
- a = self["поле"]

Чтобы передать параметры для следующей функции диалога:
- self.args = список параметров

Чтобы предварительно установить данные, назначьте словарь статическому полю data:
    class MyDialog(DialogBase):
        data = {"поле": "значение"}

Внутри функции вы можете получить:
* self.text - Команда пользователя
* self.textOrig - оригинальное произнесение команды
* self.tokens - слова в команде
* self.people - список людей в запросе
* self.airports - список аэропортов в запросе
* self.cities - список городов в запросе
* self.countries - список стран в запросе
* self.house_numbers - список номеров домов в запросе
* self.streets - список улиц в запросе
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

# Пример с сервером на Flask
Подробный пример: 
[main.py](https://github.com/MixelTe/YAlisa-dialog-helper/blob/master/main.py)
и
[dialog.py](https://github.com/MixelTe/YAlisa-dialog-helper/blob/master/dialog.py)

Краткий пример:
```py
from flask import Flask, request
from YAlisa_dialog_helper import DialogManager, DialogBase
import json


class Dialog(DialogBase):
    def start(self):
        return "Привет, как дела?", self.p2

    def p2(self):
        return "У меня всё хорошо!", False


app = Flask(__name__)
dialogManager = DialogManager(Dialog)


@app.route('/post', methods=['POST'])
def main():
    response = dialogManager.handle_dialog(request.json)
    return json.dumps(response)

```
