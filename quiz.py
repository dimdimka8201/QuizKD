# Импорт необходимых модулей Kivy и стандартных библиотек
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
import random
import json
import webbrowser

# Настройки основного окна приложения
Window.clearcolor = (0.95, 0.95, 0.99, 1)  # Цвет фона окна
Window.minimum_width = 360  # Минимальная ширина окна
Window.minimum_height = 640  # Минимальная высота окна

# Загрузка и проверка вопросов из JSON файла
try:
    with open('questions.json', 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
        # Проверка наличия обязательных полей в каждом вопросе
        required_fields = ['english', 'correctTranslation', 'wrongTranslation']
        for q in questions_data:
            if not all(field in q for field in required_fields):
                raise ValueError("Некорректная структура JSON")
        all_questions = questions_data
except Exception as e:
    print(f"Ошибка загрузки вопросов: {e}")
    all_questions = []

# Класс для стилизованных кнопок
class CenteredButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.15, 0.45, 0.8, 1)  # Синий фон
        self.background_normal = ''  # Убираем стандартный фон
        self.color = (1, 1, 1, 1)  # Белый текст
        self.bold = True  # Жирный шрифт
        self.border = (10, 10, 10, 10)  # Закругление углов
        self.halign = 'center'  # Выравнивание текста по центру
        self.valign = 'middle'

# Основной класс приложения
class QuizApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_questions = []  # Текущий список вопросов
        self.current_correct = ""  # Правильный ответ на текущий вопрос
        self.popup = None  # Переменная для хранения текущего попапа
        self.correct_answers = 0  # Счетчик правильных ответов
        self.total_questions = 0  # Общее количество вопросов
        self.game_active = True  # Флаг активности игры

    # Основной метод построения интерфейса
    def build(self):
        # Главный контейнер приложения
        self.root = FloatLayout()
        
        # Верхняя панель с счетчиками
        self.header = BoxLayout(size_hint=(1, 0.1), pos_hint={'top': 1})
        self.score_label = Label(
            text="Вопрос 0 из 0 | Правильных: 0",
            font_size=30,  # УВЕЛИЧЕННЫЙ ШРИФТ
            color=(0.12, 0.35, 0.6, 1),
            bold=True
        )
        self.header.add_widget(self.score_label)
        
        # Основная область содержимого
        self.content = FloatLayout(
            size_hint=(0.9, 0.7),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Текст текущего вопроса
        self.question_label = Label(
            text='Вопрос',
            font_size=60,  # УВЕЛИЧЕННЫЙ ШРИФТ
            color=(0.12, 0.35, 0.6, 1),
            bold=True,
            halign='center',
            valign='middle',
            size_hint=(0.9, 0.3),
            pos_hint={'center_x': 0.5, 'top': 0.95}
        )
        
        # Кнопки ответов
        self.answer1_btn = CenteredButton(
            text='Ответ 1',
            font_size=40,  # УВЕЛИЧЕННЫЙ ШРИФТ
            size_hint=(0.8, 0.2),
            pos_hint={'center_x': 0.5, 'y': 0.55}
        )
        
        self.answer2_btn = CenteredButton(
            text='Ответ 2',
            font_size=40,  # УВЕЛИЧЕННЫЙ ШРИФТ
            size_hint=(0.8, 0.2),
            pos_hint={'center_x': 0.5, 'y': 0.25}
        )
        
        # Нижняя панель с ссылкой
        self.footer = BoxLayout(size_hint=(1, 0.1), pos_hint={'y': 0})
        self.link_btn = Button(
            text='Создатель: t.me/your_telegram',
            font_size=40,  # УВЕЛИЧЕННЫЙ ШРИФТ
            color=(0.2, 0.4, 0.8, 1),
            background_color=(0, 0, 0, 0),
            underline=True
        )
        self.link_btn.bind(on_press=self.open_link)
        
        # Сборка всех элементов в интерфейс
        self.content.add_widget(self.question_label)
        self.content.add_widget(self.answer1_btn)
        self.content.add_widget(self.answer2_btn)
        self.footer.add_widget(self.link_btn)
        
        self.root.add_widget(self.header)
        self.root.add_widget(self.content)
        self.root.add_widget(self.footer)
        
        # Начальная настройка игры
        self.reset_game()
        self.answer1_btn.bind(on_press=self.check_answer)
        self.answer2_btn.bind(on_press=self.check_answer)
        
        return self.root

    # Сброс игры для нового цикла
    def reset_game(self):
        self.game_active = True
        self.correct_answers = 0
        self.current_questions = random.sample(all_questions, len(all_questions))
        self.total_questions = len(self.current_questions)
        self.next_question()

    # Отображение следующего вопроса
    def next_question(self):
        if not self.current_questions:
            self.game_active = False
            self.show_results()
            return
            
        question = self.current_questions.pop()
        answers = [question['correctTranslation'], question['wrongTranslation']]
        random.shuffle(answers)
        
        self.current_correct = question['correctTranslation']
        self.question_label.text = question['english']
        self.answer1_btn.text = answers[0]
        self.answer2_btn.text = answers[1]
        
        # Обновление счетчика
        current_num = self.total_questions - len(self.current_questions)
        self.score_label.text = f"Вопрос {current_num} из {self.total_questions} | Правильных: {self.correct_answers}"

    # Проверка ответа пользователя
    def check_answer(self, instance):
        if not self.game_active:
            return
            
        is_correct = instance.text == self.current_correct
        if is_correct:
            self.correct_answers += 1
        
        # Обновление счетчика
        current_num = self.total_questions - len(self.current_questions) + 1
        self.score_label.text = f"Вопрос {current_num} из {self.total_questions} | Правильных: {self.correct_answers}"
        
        # Создание попапа с результатом ответа
        popup_label = Label(
            text="Правильно, молодец!" if is_correct else "Не правильно, старайся лучше!",
            font_size=50,  # УВЕЛИЧЕННЫЙ ШРИФТ
            color=(1, 1, 1, 1),
            bold=True
        )
        
        self.popup = Popup(
            title='',
            content=popup_label,
            size_hint=(0.8, 0.25),
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            background_color=(0.2, 0.7, 0.3, 0.95) if is_correct else (0.8, 0.3, 0.3, 0.95),
            auto_dismiss=False
        )
                  
        # Таймеры для закрытия попапа и перехода к следующему вопросу
        self.popup.open()
        Clock.schedule_once(self.close_popup, 1.0)
        
        if self.current_questions:
            Clock.schedule_once(lambda *args: self.next_question(), 1.5)
        else:
            Clock.schedule_once(lambda *args: self.show_results(), 1.5)

    # Закрытие текущего попапа
    def close_popup(self, *args):
        if self.popup:
            self.popup.dismiss()

    # Отображение финального экрана с результатами
    def show_results(self):
        self.game_active = False
        
        # Создание макета для финального попапа
        result_layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        result_label = Label(
            text=f"Ваш счет: {self.correct_answers}/{self.total_questions}",
            font_size=50,  # УВЕЛИЧЕННЫЙ ШРИФТ
            color=(1, 1, 1, 1),
            bold=True,
            halign='center'
        )
        
        # Кнопки управления
        btn_layout = BoxLayout(size_hint=(1, 0.5), spacing=30)
        restart_btn = CenteredButton(text='Начать заново', font_size=35)
        exit_btn = CenteredButton(text='Выйти', font_size=35)
        
        restart_btn.bind(on_press=lambda *args: [self.popup.dismiss(), self.reset_game()])
        exit_btn.bind(on_press=lambda *args: App.get_running_app().stop())
        
        btn_layout.add_widget(restart_btn)
        btn_layout.add_widget(exit_btn)
        
        result_layout.add_widget(result_label)
        result_layout.add_widget(btn_layout)
        
        # Создание попапа с результатами
        self.popup = Popup(
            title='Результат',
            content=result_layout,
            size_hint=(0.9, 0.6),
            background_color=(0.15, 0.45, 0.8, 0.95),
            auto_dismiss=False
        )
        
        # Обработка закрытия попапа
        self.popup.bind(on_dismiss=self.handle_popup_dismiss)
        self.popup.open()

    # Обработка закрытия финального попапа
    def handle_popup_dismiss(self, *args):
        if not self.game_active:
            self.reset_game()

    # Открытие ссылки в браузере
    def open_link(self, instance):
        webbrowser.open("https://t.me/your_telegram")

if __name__ == '__main__':
    QuizApp().run()