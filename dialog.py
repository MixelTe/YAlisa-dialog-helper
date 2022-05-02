from random import choice
from YAlisa_dialog_helper import DialogBase

cities = {
    'москва': ['1030494/321bad1559a89db1457f', '213044/c05030fc0905b4dcb6d8'],
    'нью-йорк': ['1521359/d35dfed42c7dd95e441a', '997614/8c3e4f76e3c742b3682c'],
    'париж': ["213044/61856e3c5a5a3d509f55", '937455/c522665f5917ff13986e']
}
countries = {
    'москва': "россия",
    'нью-йорк': "сша",
    'париж': "франция",
}


class Dialog(DialogBase):
    data = {
        "cities": list(cities)
    }

    def start(self):
        return "Привет, назови своё имя", self.p2

    def p2(self):
        name, _, _ = self.FIO
        if (name == ""):
            return "Не расслышала имя. Повтори, пожалуйста!", self.p2

        self["name"] = name.title()
        self.addButtons(["Да", "Нет"])
        text = f"Приятно познакомиться, {name}. Я Алиса. Отгадаешь город по фото?"
        return text, self.p3

    def p3(self):
        if ("нет" not in self.tokens and "да" not in self.tokens):
            self.addButtons(["Да", "Нет"])
            return "Не поняла ответа! Так да или нет?", self.p3
        if ("нет" in self.tokens):
            return "Ну и ладно!", False
        if (len(self["cities"]) == 0):
            return f"{self['name']}, вы отгадали все города!", False

        self["city"] = choice(self["cities"])
        self["cities"].remove(self["city"])
        self.setCard_BigImage("Что это за город?", cities[self["city"]][0])
        return "Что это за город?", self.p4

    def p4(self, firstTry=True):
        if (self["city"] in self.cities):
            self.args = [firstTry]
            return "Правильно! А в какой стране этот город?", self.p5
        if (firstTry):
            self.args = [False]
            self.setCard_BigImage("Что это за город?", cities[self["city"]][1])
            return "Неправильно. Вот тебе дополнительное фото", self.p4
        self.addButtons(["Да", "Нет"])
        return f"Вы пытались. Это {self['city'].title()}. Сыграем ещё?", self.p3

    def p5(self, firstTry=True):
        country = countries[self["city"]]
        if (country in self.countries):
            self.addButtons(["Да", "Нет"])
            return "Правильно! Сыграем ещё?", self.p3
        if (firstTry):
            self.args = [False]
            self.setCard_BigImage("Что это за страна?", cities[self["city"]][1])
            return "Неправильно. Вот тебе дополнительное фото", self.p5
        self.addButtons(["Да", "Нет"])
        return f"Вы пытались. Это {country.title()}. Сыграем ещё?", self.p3
