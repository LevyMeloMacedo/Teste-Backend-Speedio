import requests
from bs4 import BeautifulSoup
import pymongo
import matplotlib.pyplot as plt

client = pymongo.MongoClient()
db = client['similarweb']
collection = db['sites']

def get_info(url):

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    ranking = soup.find('div', class_='wa-rank-list wa-rank-list--md').text
    site = soup.find('p', class_='wa-overview__title').text
    category = soup.find('p', class_='engagement-list__item-value').text

    avg_visit = soup.find('div', attrs={'class': 'engagement-list__item', 'data-test':"avg-visit-duration"})
    avg_visit_duration = avg_visit.find('p', attrs={'class': 'engagement-list__item-value'}).text
    
    pages_per =  soup.find('div', attrs={'class': 'engagement-list__item','data-test':"bounce-rate"})
    pages_per_visit = pages_per.find('p', attrs={'class': 'engagement-list__item-value'}).text
    
    bounce = soup.find('div', attrs={'class': 'engagement-list__item','data-test':"bounce-rate"})
    bounce_rate = bounce.find('p', attrs={'class': 'engagement-list__item-value'}).text
    main_countries = [country.text for country in soup.find_all('p', class_='engagement-list__item-value')]

    gender_distribution = soup.find('ul', class_='wa-demographics__gender-legend').text

   

    age_distribution = [int(value) for value in soup.find_all('d', class_='highcharts-679lgvi-234')]

    data = {
        'ranking': ranking,
        'site': site,
        'category': category,
        'avg_visit_duration': avg_visit_duration,
        'pages_per_visit': pages_per_visit,
        'bounce_rate': bounce_rate,
        'main_countries': main_countries,
        'gender_distribution': gender_distribution,
        'age_distribution': age_distribution,
    }

    collection.insert_one(data)

    return data


def save_info(url):

    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print(e)
        return 400

    soup = BeautifulSoup(response.content, 'html.parser')

    data = get_info(url)

    collection.insert_one(data)

    return 201

def get_info_by_url(url):

    try:
        data = collection.find_one({'site': url})
    except pymongo.errors.NotFound as e:
        print(e)
        return 404

    return data

def main():

    url_base = 'https://www.similarweb.com/top-websites/'
    url = requests.get(url_base + input('Site deseja acessar? '))
    info = get_info(url)
    print(info)

if __name__ == '__main__':
    main()

