import requests
from bs4 import BeautifulSoup
from flask import Flask

HOST = '127.0.0.1'
PORT = 5000
HABRA_HTTPS_URL = 'https://habrahabr.ru/'
HABRA_HTTP_URL = 'http://habrahabr.ru/'
LOCAL_URL = 'http://{host}:{port}/'.format(host=HOST, port=PORT)
BAD_TAGS = ('[document]', 'head', 'style', 'script')

app = Flask(__name__)


def is_not_number(str):
    try:
        float(str.replace(',', '.'))
        return False
    except ValueError:
        return True


def replace_it(item):
    words = item.split()
    for position, word in enumerate(words):
        clean_word = word.strip('.,:!@#$%^&*()_-')
        if len(clean_word) == 6 and is_not_number(word):
            words[position] = word.replace(clean_word, clean_word + "\u2122")
    return ' '.join(words)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def root_query(path):
    url = '{}{}'.format(HABRA_HTTPS_URL, path)
    r = requests.get(url)

    if path.split('/')[0] == 'fonts':
        return r.__dict__.get('_content')

    response = r.text.replace(HABRA_HTTPS_URL, LOCAL_URL)
    response = response.replace(HABRA_HTTP_URL, LOCAL_URL)

    soup = BeautifulSoup(response, 'html.parser')
    content = soup.findAll(text=True)
    for item in content:
        if item.parent.name not in BAD_TAGS:
            replace_result = replace_it(item)
            item.replaceWith(replace_result)
    return soup.prettify()


if __name__ == '__main__':
    app.run(debug=False, host=HOST, port=PORT)