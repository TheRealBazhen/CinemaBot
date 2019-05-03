import urllib.request
import urllib.parse
from app import config
from lxml import html as html_parser
from io import StringIO


def get_man_id_by_name(name):
    params = {'kp_query': name.lower(), 'what': ''}
    url = 'https://www.kinopoisk.ru/index.php?' + urllib.parse.urlencode(params)
    try:
        response = urllib.request.urlopen(url)
        html = response.read()
        html = html.decode('utf-8')
        tree = html_parser.parse(StringIO(html))
        div = tree.xpath('//div[@class="element most_wanted"]/p/a')
        if len(div) < 1:
            return None
        div = div[0]
        href = div.attrib['href'].split('/')
        if href[1] != 'name':
            return None
        return href[2]
    except Exception as e:
        print('Error getting html: ' + str(e))
        return None


def get_film_list_by_url(url):
    try:
        response = urllib.request.urlopen(url)
        html = response.read()
        html = html.decode('utf-8')
        tree = html_parser.parse(StringIO(html))
        film_data = tree.xpath('//div[@class="element"]')
        film_data += tree.xpath('//div[@class="element width_2"]')
        films = []
        for i, f in enumerate(film_data):
            div = f.xpath('//div[@class="right"]/div')
            rating = '0.0'
            if len(div) > i:
                rating = div[i].text
            div = f.xpath('//div[@class="info"]/p[@class="name"]/a')
            title = div[i].text
            films.append((title, rating))
        return films
    except Exception as e:
        print('Error getting html: ' + str(e))
        return None


def get_film_list_by_director_id(director_id):
    params = {'m_act[what]': 'content',
              'm_act[creator_array]': 'director:' + str(director_id)}
    url = config['parser']['director_url'] + urllib.parse.urlencode(params)
    return get_film_list_by_url(url)


def get_film_list_by_genre(genre_code):
    url = config['parser']['genre_url'].format(genre_code)
    return get_film_list_by_url(url)
