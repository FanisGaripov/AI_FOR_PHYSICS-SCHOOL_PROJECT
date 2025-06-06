from flask import Flask, render_template, request, Response, stream_with_context, session, send_from_directory
import g4f
import time
import requests, re
from bs4 import BeautifulSoup
import os
import json
import random
from others import labs

app = Flask(__name__)
app.secret_key = 'supersecretkey'


@app.route('/')
def hello():
    # главная страница, которую видит пользователь при входе
    return render_template('main.html')


def load_tasks_from_files(number):
    # загрузка заданий ФИПИ из файлов
    catalog = {}
    if number == 1:
        tasks_dir = 'База заданий ОГЭ'
    else:
        tasks_dir = 'База заданий ЕГЭ'

    for filename in os.listdir(tasks_dir):
        if filename.startswith('tasks_type_') and filename.endswith('.json'):
            theme = filename.replace('tasks_type_', '').replace('.json', '')
            try:
                with open(os.path.join(tasks_dir, filename), 'r', encoding='utf-8') as f:
                    tasks = json.load(f)
                    catalog[theme] = tasks
            except Exception as e:
                print(f"Ошибка загрузки файла {filename}: {e}")

    return catalog


# каталоги заданий огэ и егэ помещаются в переменные для дальнейшей передачи в функциях каталогов
oge_catalog = load_tasks_from_files(1)
ege_catalog = load_tasks_from_files(2)


@app.route('/physics-chatbot', methods=['GET', 'POST'])
def index():
    # страница с чат-ботом
    return render_template('index.html')


@app.route('/contact')
def contact():
    # страница с моими контактами, функционально не несет какой-то пользы
    return render_template('contact.html')


@app.route('/glossarium')
def glossarium():
    return render_template('glossarium.html')


@app.route('/simulations', methods=['GET', 'POST'])
def simulations():
    experiments_data = {
        'blackbody-spectrum_ru': 'Спектр абсолютно чёрного тела',
        'build-a-nucleus_ru': 'Построение атомного ядра',
        'build-an-atom_ru': 'Построение атома',
        'buoyancy-basics_en': 'Основы плавучести',
        'color-vision_ru': 'Цветовое зрение',
        'density_ru': 'Плотность',
        'diffusion_ru': 'Диффузия',
        'faradays-electromagnetic-lab_en': 'Лаборатория электромагнетизма Фарадея',
        'gas-properties_ru': 'Свойства газов',
        'gases-intro_ru': 'Введение в газы',
        'generator_en': 'Генератор',
        'geometric-optics-basics_en': 'Геометрическая оптика (основы)',
        'magnets-and-electromagnets_en': 'Магниты и электромагниты',
        'masses-and-springs_ru': 'Массы и пружины',
        'models-of-the-hydrogen-atom_en': 'Модели атома водорода',
        'ohms-law_ru': 'Закон Ома',
        'pendulum-lab_ru': 'Лаборатория маятника',
        'resistance-in-a-wire_ru': 'Сопротивление в проводе',
        'sound-waves_en': 'Звуковые волны',
        'states-of-matter_ru': 'Агрегатные состояния вещества',
        'under-pressure_ru': 'Под давлением'
    }

    # Для обратной совместимости сохраняем и исходный список
    all_experiments = list(experiments_data.keys())

    return render_template(
        'simulations.html',
        all_experiments=all_experiments,
        experiments_data=experiments_data
    )


@app.route('/simulations/<exp_name>', methods=['GET', 'POST'])
def simulation_page(exp_name):
    # страница для каждого эксперимента(отдельная)
    return send_from_directory('templates/simulations', f'{exp_name}.html')


@app.route('/ege', methods=['GET', 'POST'])
def EGE_catalog():
    # каталог егэ
    return render_template('ege_catalog.html', catalog=ege_catalog)


@app.route('/oge', methods=['GET', 'POST'])
def OGE_catalog():
    # каталог огэ
    return render_template('oge_catalog.html', catalog=oge_catalog)


def parse_experiments(text):
    # функция для парсинга экспериментов с efizika.ru
    categories = {}
    current_category = None

    # Разбиваем текст на строки
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    i = 0
    while i < len(lines):
        line = lines[i]

        # Проверяем, является ли строка заголовком категории
        if line.endswith(':'):
            current_category = line[:-1]
            categories[current_category] = []
            i += 1
            # Пропускаем строку "Список экспериментов:" если она есть
            if i < len(lines) and lines[i] == "Список экспериментов:":
                i += 1
            continue

        # Парсим номер и название эксперимента
        exp_match = re.match(r'(\d+)\.\s+(\d+)\.\s+(.+)$', line)
        if exp_match:
            exp_num = exp_match.group(2)
            exp_title = exp_match.group(3)
            exp_url = None

            # Проверяем следующую строку на наличие URL
            if i + 1 < len(lines) and lines[i + 1].startswith('Ссылка:'):
                url_match = re.match(r'Ссылка:\s+(https?://\S+)', lines[i + 1])
                if url_match:
                    exp_url = url_match.group(1)
                    i += 1  # Пропускаем строку с URL

            categories[current_category].append({
                'num': exp_num,
                'title': exp_title,
                'url': exp_url
            })
        i += 1

    return categories


@app.route('/yandex_39563c53a7f880d4.html')
def ya():
    return render_template('yandex_39563c53a7f880d4.html')


@app.route('/experiments')
def experiments():
    # страница с экспериментами
    stroka = labs
    experiments_data = parse_experiments(stroka)
    total_experiments = sum(len(exps) for exps in experiments_data.values())

    return render_template('experiments.html',
                           experiments=experiments_data,
                           total_experiments=total_experiments)


def process_catalog(raw_catalog):
    # я хз че это, видимо мне это чатгпт написал и она вроде нигде не используется :))))
    main_topics = []
    other_topics = []

    for topic in raw_catalog:
        if isinstance(topic, dict) and 'topic_id' in topic and 'topic_name' in topic and 'categories' in topic:
            if str(topic['topic_id']).isdigit():
                main_topics.append(topic)
            else:
                other_topics.append(topic)

    main_topics.sort(key=lambda x: int(x['topic_id']))

    return {
        'main_topics': main_topics,
        'other_topics': other_topics
    }


@app.route('/ege/<category>')
def EGE_zadaniya(category):
    # задания егэ
    tasks = ege_catalog.get(category, [])
    return render_template('EGE.html', category=category, tasks=tasks)


@app.route('/oge/<category>')
def OGE_zadaniya(category):
    # задания огэ
    tasks = oge_catalog.get(category, [])
    return render_template('OGE.html', category=category, tasks=tasks)


def get_catalog(ege):
    # функция получения каталог с решу егэ, взята была из библиотеки sdamgia, но в настоящий момент не используется по причине авторских прав на задачи
    if ege is True:
        doujin_page = requests.get(
            f'https://phys-ege.sdamgia.ru/prob_catalog')
    else:
        doujin_page = requests.get(
            f'https://phys-oge.sdamgia.ru/prob_catalog')
    soup = BeautifulSoup(doujin_page.content, 'html.parser')
    catalog = []
    CATALOG = []

    for i in soup.find_all('div', {'class': 'cat_category'}):
        try:
            i['data-id']
        except:
            catalog.append(i)

    for topic in catalog[1:]:
        TOPIC_NAME = topic.find(
            'b', {'class': 'cat_name'}).text.split('. ')[1]
        TOPIC_ID = topic.find(
            'b', {'class': 'cat_name'}).text.split('. ')[0]
        if TOPIC_ID[0] == ' ':
            TOPIC_ID = TOPIC_ID[2:]
        if TOPIC_ID.find('Задания ') == 0:
            TOPIC_ID = TOPIC_ID.replace('Задания ', '')

        CATALOG.append(
            dict(
                topic_id=TOPIC_ID,
                topic_name=TOPIC_NAME,
                categories=[
                    dict(
                        category_id=i['data-id'],
                        category_name=i.find(
                            'a', {'class': 'cat_name'}).text
                    )
                    for i in
                    topic.find('div', {'class': 'cat_children'}).find_all('div', {'class': 'cat_category'})]
            )
        )

    return CATALOG


def get_category_by_id(categoryid, ege, page=1):
    # тоже самое, что и с предыдущей функцией
    if ege is True:
        doujin_page = requests.get(
            f'https://phys-ege.sdamgia.ru/test?&filter=all&theme={categoryid}&page={page}')
        soup = BeautifulSoup(doujin_page.content, 'html.parser')
        zadaniya = str(soup.find_all('p', {'class': 'left_margin'}))[1:-2]
        modified_text = re.sub(r'src="/', r'src="https://phys-ege.sdamgia.ru/', zadaniya)
    else:
        doujin_page = requests.get(
            f'https://phys-oge.sdamgia.ru/test?&filter=all&theme={categoryid}&page={page}')
        soup = BeautifulSoup(doujin_page.content, 'html.parser')
        zadaniya = str(soup.find_all('p', {'class': 'left_margin'}))[1:-2]
        modified_text = re.sub(r'src="/', r'src="https://phys-oge.sdamgia.ru/', zadaniya)

    return modified_text


@app.route('/spisok-formul-po-fizike')
def spisok_formul_po_fizike():
    # страница со всеми формулами по физике. для написания формул использован mathjax(js)
    return render_template('spisok_formul.html')


@app.route('/aboutme')
def aboutme():
    # страница обо мне, тоже функционально не несет никакой пользы
    return render_template('aboutme.html')


# а дальше начинаются 3 функции для работы с ИИ:
# 1 и 2 Занимаются потоковым выводом
# 3 получает ответ от ИИ, тоже в потоковом виде

@app.route('/stream')
def stream():
    question = request.args.get('question')
    response = ask_physics_question(question)
    return Response(stream_with_context(response_stream(response)), content_type='text/event-stream')


def response_stream(response):
    for chunk in response:
        if isinstance(chunk, str):
            yield f"data: {chunk}\n\n"


def ask_physics_question(question):
    """Функция для отправки вопроса ИИ и получения ответа с потоковым выводом."""
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-4",  # Модель ИИ
            messages=[{"role": "system", "content": "Ты помощник, который отвечает только на вопросы по физике ЕГЭ. экзаменам, вопросы напрямую связанные с физиикой. Если это другая тема, отвечай так: Это тема не относится к физике, задайте другой вопрос."},
                      {"role": "user", "content": question}],
            stream=True  # Включаем потоковый вывод
        )
        for chunk in response:
            if isinstance(chunk, str):
                yield chunk
    except Exception as e:
        yield f"Произошла ошибка: {e}"



@app.route('/minigame', methods=['GET', "POST"])
def minigame_with_problems_generator():
    answer = ''
    if 'answer_list' not in session:
        session['answer_list'] = ''
        session.modified = True
    try:
        if request.method == 'POST':
            answer_check = request.form.get('answer')
            if answer_check == session['answer_list']:
                itog = 'Верно'
            else:
                itog = f'Неверно, ответ: {session["answer_list"]}'
            answer, zadacha = generate_problem()
            while 'Решение' in zadacha or 'Решение' in answer:
                answer, zadacha = generate_problem()
            session['answer_list'] = answer
            if answer and zadacha:
                return render_template('minigame.html', zadacha=zadacha, itog=itog)
        elif request.method == 'GET':
            answer, zadacha = generate_problem()
            while 'Решение' in zadacha or 'Решение' in answer:
                answer, zadacha = generate_problem()
            session['answer_list'] = answer
            if answer and zadacha:
                return render_template('minigame.html', zadacha=zadacha)
    except Exception as e:
        return f"Ошибка: {str(e)}"


def generate_problem():
    try:
        answer = ''
        zadacha = ''
        client = g4f.Client()
        razdel_spisok = ['механике', 'термодинамике', 'электродинамике', 'оптике', 'квантовой физике', 'ядерной физике']
        razdel_number = random.randint(0, 5)
        razdel = razdel_spisok[razdel_number]
        chat_completion = client.chat.completions.create(model="gpt-4",
                                                         messages=[{"role": "system",
                                                                    "content": "Ты помощник, который генерирует простые задачи по физике. Тебе нужно выслать сообщение вот в таком формате: Задача: (сюда пишешь задачу), ответ:(сюда пишешь ответ, только число без пробелов и других знаков). Решение НЕ НУЖНО. Больше ничего не пиши. Вот темы, на которые ты можешь генерировать задачи: механика, термодинамика, электродинамика, оптика, квантовая физика, ядерная физика"},
                                                                   {"role": "user", "content": f'Сгенерируй задачу по {razdel}'}])
        if chat_completion.choices:
            zadacha = chat_completion.choices[0].message.content or ""
            if 'Ответ' in zadacha:
                answer = zadacha.split('Ответ:')[1].strip()
                zadacha = zadacha.split('Ответ:')[0].strip()
            elif 'ответ' in zadacha:
                answer = zadacha.split('ответ:')[1].strip()
                zadacha = zadacha.split('ответ:')[0].strip()
        else:
            raise Exception("Ответ не найден в сгенерированной задаче.")
        return answer, zadacha
    except Exception as e:
        print(f"Ошибка при генерации задачи: {str(e)}")


# @app.route('/test', methods=['GET', 'POST'])
# def random_test_api():
#     test = requests.get('https://opentdb.com/api.php?amount=10&category=17&difficulty=easy&type=multiple')


# материалы по физике
# основные темы: механика, термодинамика, электродинамика, оптика, квантовая физика, ядерная физика
# и страницы этих тем

@app.route('/materials')
def materials():
    return render_template('materials.html')


@app.route('/materials/mechanics')
def materials_mechanics():
    return render_template('materials_mechanics.html')


@app.route('/materials/thermodynamics')
def materials_thermodynamics():
    return render_template('materials_thermodynamics.html')


@app.route('/materials/electrodynamics')
def materials_electrodynamics():
    return render_template('materials_electrodynamics.html')


@app.route('/materials/optics')
def materials_optics():
    return render_template('materials_optics.html')


@app.route('/materials/quantum')
def materials_quantum():
    return render_template('materials_quantum.html')


@app.route('/materials/nuclear')
def materials_nuclear():
    return render_template('materials_nuclear.html')



if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=True)
