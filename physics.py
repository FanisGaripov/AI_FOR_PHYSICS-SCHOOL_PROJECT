from flask import Flask, render_template, request, Response, stream_with_context
import g4f
import time
import requests, re
from bs4 import BeautifulSoup
import os
import json

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template('main.html')


def load_tasks_from_files(number):
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


oge_catalog = load_tasks_from_files(1)
ege_catalog = load_tasks_from_files(2)


@app.route('/physics-chatbot', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/ege', methods=['GET', 'POST'])
def EGE_catalog():
    return render_template('ege_catalog.html', catalog=ege_catalog)


@app.route('/oge', methods=['GET', 'POST'])
def OGE_catalog():
    return render_template('oge_catalog.html', catalog=oge_catalog)


def parse_experiments(text):
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
    stroka = '''Механика:
Список экспериментов:
2. 02. Измерение ускорения свободного падения на телах Солнечной системы
   Ссылка: http://efizika.ru/html5/02/index.html
3. 05. Определение коэффициента трения при помощи наклонной плоскости
   Ссылка: http://efizika.ru/html5/05/index.html
4. 06. Проверка закона сохранения механической энергии
   Ссылка: https://efizika.ru/html5/06/index.html
5. 07. Нахождение коэффициента трения методом предельного угла
   Ссылка: http://efizika.ru/html5/07/index.html
6. 08. Определение ускорения свободного падения на телах Солнечной системы при помощи машины Атвуда
   Ссылка: http://efizika.ru/html5/08/index.html
7. 16. Определение КПД при подъёме тела по наклонной плоскости
   Ссылка: https://efizika.ru/html5/16/index.html
8. 21. Баллистический маятник. Неупругий удар
   Ссылка: https://efizika.ru/html5/21/index.html
9. 34. Определение выталкивающей силы, действующей на погруженное в жидкость тело
   Ссылка: https://efizika.ru/html5/34/index.html
10. 36. Выяснение условий плавания тел
   Ссылка: https://efizika.ru/html5/36/index.html
11. 38. Градуирование пружины и измерение сил динамометром
   Ссылка: https://efizika.ru/html5/38/index.html
12. 42. Проверка постоянства отношения ускорений двух тел при их взаимодействии
   Ссылка: https://efizika.ru/html5/42/index.html
13. 104. Измерение жесткости пружины на основе закономерностей колебаний пружинного маятника
   Ссылка: http://efizika.ru/html5/104/index.html
14. 107. Исследование равноускоренного движения без начальной скорости
   Ссылка: https://efizika.ru/html5/107/index.html
15. 114. Изучение движения тела, брошенного под углом к горизонту
   Ссылка: http://efizika.ru/html5/114/index.html
16. 118. Изучение движения тела, брошенного горизонтально
   Ссылка: http://efizika.ru/html5/118/index.html
17. 123. Измерение линейных размеров малых тел
   Ссылка: http://efizika.ru/html5/123/index.html
18. 131. Баллистический маятник. Упругий удар
   Ссылка: https://efizika.ru/html5/131/index.html
19. 132. Определение коэффициента вязкости жидкости по методу Стокса
   Ссылка: https://efizika.ru/html5/132/index.html
20. 133. Определение скорости пули c помощью пружинного маятника. Непругий удар
   Ссылка: https://efizika.ru/html5/133/index.html
21. 139. Определение скорости пули c помощью пружинного маятника. Упругий удар
   Ссылка: https://efizika.ru/html5/139/index.html
22. 144. Определение модуля Юнга из деформации изгиба стержня
   Ссылка: http://efizika.ru/html5/144/index.html
23. 146. Определение коэффициента трения методом вращающихся блоков
   Ссылка: https://efizika.ru/html5/146/index.html
24. 168. Определение коэффициента упругости и модуля упругости при деформации растяжения
   Ссылка: http://efizika.ru/html5/168/index.html
25. 169. Изучение вращательного движения твёрдого тела на приборе Обербека
   Ссылка: http://efizika.ru/html5/169/index.html
26. 181. Измерение массы тела рычажными весами
   Ссылка: https://efizika.ru/html5/181/index.html
27. 182. Выяснение условий равновесия рычага
   Ссылка: http://efizika.ru/html5/182/index.html
28. 187. Измерение массы тела на разноплечих весах
   Ссылка: https://efizika.ru/html5/187/index.html
29. 189. Определение плотности вещества
   Ссылка: https://efizika.ru/html5/189/index.html
30. 213. Измерение массы тела при помощи рычажных и электронных весов
   Ссылка: https://efizika.ru/html5/213/index.html
31. 225. Выяснение условий плавания тела в жидкости
   Ссылка: https://efizika.ru/html5/225/index.html
32. 258. Исследование движения тела по гладкой поверхности под действием постоянной силы
   Ссылка: https://efizika.ru/
33. 259. Исследование движения тела по шероховатой поверхности под действием постоянной силы
   Ссылка: https://efizika.ru/html5/259/index.html
34. 282. Выяснение условий равновесия рычага
   Ссылка: https://efizika.ru/html5/282/index.html
Молекулярная физика:
Список экспериментов:
2. 11. Определение удельной теплоемкости металлов
   Ссылка: http://efizika.ru/html5/11/index.html
3. 12. Определение удельной теплоемкости воды
   Ссылка: http://efizika.ru/html5/12/index.html
4. 15. Определение удельной теплоемкости твердых тел
   Ссылка: http://efizika.ru/html5/15/index.html
5. 17. Определение удельной теплоты плавления льда
   Ссылка: http://efizika.ru/html5/17/index.html
6. 18. Исследование изобарного процесса в газах
   Ссылка: http://efizika.ru/html5/18/index.html
7. 19. Экспериментальное нахождение удельной теплоты сгорания топлива
   Ссылка: http://efizika.ru/html5/19/index.html
8. 22. Определение молярной массы газа
   Ссылка: http://efizika.ru/html5/22/index.html
9. 23. Определение универсальной газовой постоянной
   Ссылка: http://efizika.ru/html5/23/index.html
10. 24. Изучение изотермического процесса в газах
   Ссылка: http://efizika.ru/html5/24/index.html
11. 25. Изучение изохорного процесса в газах
   Ссылка: http://efizika.ru/html5/25/index.html
12. 26. Определение удельной теплоемкости жидкостей методом электрокалориметра
   Ссылка: http://efizika.ru/html5/26/index.html
13. 27. Определение постоянной Больцмана
   Ссылка: http://efizika.ru/html5/27/index.html
14. 28. Наблюдение за охлаждением воды при её испарении и определение влажности воздуха
   Ссылка: http://efizika.ru/html5/28/index.html
15. 29. Изучение расширения твердых тел
   Ссылка: http://efizika.ru/html5/29/index.html
16. 30. Экспериментальное нахождение массы воды в мокром снеге
   Ссылка: https://efizika.ru/html5/30/index.html
17. 31. Определение удельной теплоты парообразования воды
   Ссылка: https://efizika.ru/html5/31/index.html
18. 33. Сравнение количеств теплоты при смешивании воды разной температуры
   Ссылка: http://efizika.ru/html5/33/index.html
19. 101. Экспериментальное определение удельных теплоемкостей различных жидкостей
   Ссылка: https://efizika.ru/html5/101/index.html
20. 103. Определение коэффициента полезного действия электрического нагревателя воды
   Ссылка: http://efizika.ru/html5/103/index.html
21. 164. Определение КПД теплового процесса при сгорании твёрдого топлива
   Ссылка: https://efizika.ru/html5/164/index.html
22. 184. Определение удельной теплоты сгорания топлива
   Ссылка: http://efizika.ru/html5/184/index.html
24. 215. Определение удельной теплоемкости твердых тел
   Ссылка: https://efizika.ru/html5/215/index.html
25. 218. Исследование изобарного процесса в газах
   Ссылка: https://efizika.ru/html5/218/index.html
Электричество и магнетизм:
Список экспериментов:
2. 09. Измерение ЭДС и внутреннего сопротивления источника тока
   Ссылка: http://efizika.ru/html5/09/index.html
3. 10. Определение заряда электрона и числа Фарадея
   Ссылка: http://efizika.ru/html5/10/index.html
4. 35. Изучение явления электромагнитной индукции
   Ссылка: https://efizika.ru/html5/35/index.html
5. 37. Наблюдение действия магнитного поля на проводник с током
   Ссылка: http://efizika.ru/html5/37/index.html
6. 103. Определение коэффициента полезного действия электрического нагревателя воды
   Ссылка: http://efizika.ru/html5/103/index.html
7. 106. Измерение сопротивления проводника при помощи амперметра и вольтметра
   Ссылка: http://efizika.ru/html5/106/index.html
8. 108. Определение удельного сопротивления металлического проводника (схема 2)
   Ссылка: http://efizika.ru/html5/108/index.html
9. 109. Определение температурного коэффициента сопротивления металлов
   Ссылка: http://efizika.ru/html5/109/index.html
10. 116. Определение удельного сопротивления металлического проводника (схема 1)
   Ссылка: http://efizika.ru/html5/116/index.html
11. 134. Определение горизонтальной составляющей магнитного поля Земли с помощью тангенс–буссоли
   Ссылка: https://efizika.ru/html5/134/index.html
12. 138. Определение числа витков во вторичной обмотке трансформатора
   Ссылка: https://efizika.ru/html5/138/index.html
13. 140. Измерение сопротивления проводников методом амперметров
   Ссылка: https://efizika.ru/html5/140/index.html
14. 141. Измерение сопротивления резисторов методом вольтметров
   Ссылка: https://efizika.ru/html5/141/index.html
15. 142. Регулирование силы тока реостатом
   Ссылка: http://efizika.ru/html5/142/index.html
16. 143. Измерение силы тока амперметром
   Ссылка: https://efizika.ru/html5/143/index.html
17. 153. Изучение законов последовательного соединений проводников
   Ссылка: http://efizika.ru/html5/153/index.html
18. 148. Измерение напряжения на различных участках электрической цепи
   Ссылка: https://efizika.ru/html5/148/index.html
19. 156. Определение емкости конденсатора в цепи переменного тока
   Ссылка: http://efizika.ru/html5/156/index.html
20. 157. Определение индуктивности катушки в цепи переменного тока
   Ссылка: http://efizika.ru/html5/157/index.html
21. 179. Изучение действия электромагнита
   Ссылка: https://efizika.ru/html5/179/index.html
22. 177. Исследование смешанного соединения проводников
   Ссылка: https://efizika.ru/html5/177/index.html
23. 185. Исследование взаимодействия тока с постоянным магнитом
   Ссылка: https://efizika.ru/html5/185/index.html
24. 188. Исследование зависимости мощности, потребляемой лампой накаливания от напряжения на ее зажимах
   Ссылка: https://efizika.ru/html5/188/index.html
25. 192. Изучение параллельного соединения проводников
   Ссылка: https://efizika.ru/html5/192/index.html
26. 252. Исследование работы  простейшего генератора переменного тока
   Ссылка: https://efizika.ru/html5/252/index.html
Колебания и волны:
Список экспериментов:
2. 01. Изучение колебаний математического маятника
   Ссылка: https://efizika.ru/html5/01/index.html
3. 03. Изучение колебаний пружинного маятника
   Ссылка: http://efizika.ru/html5/03/index.html
4. 102. Изучение колебаний тела на поверхности жидкости
   Ссылка: https://efizika.ru/html5/102/index.html
5. 104. Измерение жесткости пружины на основе закономерностей колебаний пружинного маятника
   Ссылка: http://efizika.ru/html5/104/index.html
6. 113. Сложение взаимноперпендикулярных колебаний. Фигуры Лиссажу
   Ссылка: http://efizika.ru/html5/113/index.html
7. 129. Колебания тела на границе несмешивающихся жидкостей с различной плотностью
   Ссылка: https://efizika.ru/html5/129/index.html
8. 130. Колебания жидкости в сообщающихся сосудах U-образной формы
   Ссылка: https://efizika.ru/html5/130/index.html
9. 136. Исследование колебаний тела на поверхности жидкости
   Ссылка: https://efizika.ru/html5/136/index.html
10. 137. Определение плотности жидкости с помощью исследования колебаний тела на её поверхности
   Ссылка: https://efizika.ru/html5/137/index.ru
11. 145. Изучение гармонических колебаний цепи на блоках
   Ссылка: https://efizika.ru/html5/145/index.html
12. 146. Определение коэффициента трения методом вращающихся блоков
   Ссылка: https://efizika.ru/html5/146/index.html
13. 147. Электрические колебания заряженного тела
   Ссылка: https://efizika.ru/html5/147/index.html
14. 152. Гармонические колебания поршня в герметично закрытом с обоих сторон цилиндре
   Ссылка: http://efizika.ru/html5/152/index.html
15. 158. Исследование колебаний пружинного маятника
   Ссылка: https://efizika.ru/html5/158/index.html
16. 161. Изучение колебаний маятника из двух параллельно соединенных пружин
   Ссылка: https://efizika.ru/html5/161/index.html
17. 162. Изучение колебаний маятника из двух последовательно соединенных пружин
   Ссылка: https://efizika.ru/
18. 163. Определение скорости звука методом сдвига фаз
   Ссылка: https://efizika.ru/html5/163/index.html
19. 201. Определение ускорения свободного падения с помощью математического маятника
   Ссылка: http://efizika.ru/html5/201/index.html
20. 202. Определение ускорения свободного падения с помощью физического маятника (стержень)
   Ссылка: https://efizika.ru/html5/202/index.html
21. 203. Изучение колебаний физического маятника (груз на стержне)
   Ссылка: https://efizika.ru/html5/203/index.html
22. 248. Изучение колебаний квадратной рамки с током в магнитном поле
   Ссылка: https://efizika.ru/html5/248/index.html
23. 249. Исследование колебаний квадратной рамки с током в магнитном поле
   Ссылка: https://efizika.ru/html5/249/index.html
24. 250. Определение магнитной индукции постоянного магнита методом колебаний квадратной рамки с током
   Ссылка: https://efizika.ru/html5/250/index.html
Оптика:
Список экспериментов:
2. 04. Определение длины световой волны с помощью дифракционной решётки
   Ссылка: http://efizika.ru/html5/04/index.html
3. 39. Изучение закона преломления света
   Ссылка: https://efizika.ru/html5/39/index.html
4. 117. Изучение закона отражения света
   Ссылка: http://efizika.ru/html5/117/index.html
5. 135. Исследование закона Малюса
   Ссылка: https://efizika.ru/html5/135/index.html
6. 150. Определение показателя преломления вещества
   Ссылка: http://efizika.ru/html5/150/index.html
7. 165. Изучение закона полного отражения
   Ссылка: http://efizika.ru/html5/165/index.html
8. 173. Определение показателя преломления жидкостей при помощи рефрактометра»
   Ссылка: https://efizika.ru/html5/173/index.html
9. 174. Определение концентрации растворов хлорида натрия при помощи рефрактометра
   Ссылка: https://efizika.ru/html5/174/index.html
10. 193. Изучение закона полного отражения света
   Ссылка: https://efizika.ru/html5/193/index.html
11. 194. Измерение показателя преломления вещества
   Ссылка: https://efizika.ru/html5/194/index.html
12. 214. Изучение зависимости освещенности объекта от расстояния до источника света
   Ссылка: https://efizika.ru/html5/214/index.html
Квантовая и атомная физика:
Список экспериментов:
2. 110. Изучение зависимости сопротивления полупроводников от температуры и определение ширины запрещенной зоны
   Ссылка: https://efizika.ru/html5/110/index.html
3. 120. Исследование излучения абсолютно чёрного тела
   Ссылка: https://efizika.ru/html5/120/index.html
4. 154. Определение постоянной Планка
   Ссылка: http://efizika.ru/html5/154/index.html
5. 170. Изучение сплошного и линейчатого спектров
   Ссылка: https://efizika.ru/html5/170/index.html
6. 171. Наблюдение спектров испускания
   Ссылка: https://efizika.ru/html5/171/index.html
7. 172. Определение температуры нагретых тел с помощью оптического пирометра
   Ссылка: https://efizika.ru/html5/172/index.html
8. 176. Определение постоянной Планка
   Ссылка: https://efizika.ru/html5/176/index.html
9. 186. Определение постоянной Планка
   Ссылка: https://efizika.ru/html5/186/index.html
10. 195. Исследование линейчатых спектров
   Ссылка: https://efizika.ru/html5/195/index.html'''
    experiments_data = parse_experiments(stroka)
    total_experiments = sum(len(exps) for exps in experiments_data.values())

    return render_template('experiments.html',
                           experiments=experiments_data,
                           total_experiments=total_experiments)


def process_catalog(raw_catalog):
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
    tasks = ege_catalog.get(category, [])
    return render_template('EGE.html', category=category, tasks=tasks)


@app.route('/oge/<category>')
def OGE_zadaniya(category):
    tasks = oge_catalog.get(category, [])
    return render_template('OGE.html', category=category, tasks=tasks)


def get_catalog(ege):
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


# print(get_catalog())
# print(get_category_by_id(204))

# html_content = str(get_category_by_id(204))
# soup = BeautifulSoup(html_content, 'html.parser')
#
# for script in soup(["script", "style"]):  # Удаляем скрипты и стили
#     script.decompose()
#
# # Извлекаем только текст и изображения
# text_and_images = []
# for element in soup.find_all(['p', 'img']):
#     if element.name == 'p':
#         text_and_images.append(element.get_text(strip=True))
#     elif element.name == 'img':
#         text_and_images.append(element['src'])  # Добавляем только ссылку на изображение

# # Выводим результат
# for item in text_and_images:
#     print(item)


@app.route('/spisok-formul-po-fizike')
def spisok_formul_po_fizike():
    return render_template('spisok_formul.html')


@app.route('/aboutme')
def aboutme():
    return render_template('aboutme.html')


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


if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=True)
