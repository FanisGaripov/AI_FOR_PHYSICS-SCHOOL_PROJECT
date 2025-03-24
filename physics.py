from flask import Flask, render_template, request, Response, stream_with_context
import g4f
import time
import requests, re
from bs4 import BeautifulSoup

app = Flask(__name__)


@app.route('/physics-chatbot', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/EGE')
def EGE():
    return render_template('EGE.html', zadaniya=get_category_by_id(204))


def get_catalog():
    doujin_page = requests.get(
        f'https://phys-ege.sdamgia.ru/prob_catalog')
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


def get_category_by_id(categoryid, page=1):
    doujin_page = requests.get(
        f'https://phys-ege.sdamgia.ru/test?&filter=all&theme={categoryid}&page={page}')
    soup = BeautifulSoup(doujin_page.content, 'html.parser')
    zadaniya = str(soup.find_all('p', {'class': 'left_margin'}))[1:-2]
    print(zadaniya)
    modified_text = re.sub(r'src="/', r'src="https://phys-ege.sdamgia.ru/', zadaniya)

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
    """
    Функция для отправки вопроса ИИ и получения ответа с потоковым выводом.
    """
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
                print(chunk)
    except Exception as e:
        yield f"Произошла ошибка: {e}"


if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=True)