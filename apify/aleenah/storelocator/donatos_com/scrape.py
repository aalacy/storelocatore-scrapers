import csv
import re
from bs4 import BeautifulSoup
import requests

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states=[]
    cities = []
    types=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids=[]
    page_url=[]

    res=requests.get("https://www.donatos.com/locations/all")
    soup = BeautifulSoup(res.text, 'html.parser')
    lis = soup.find('div', {'id': 'locationresults'}).find_all('li')

    for li in lis:
        addr=li.find('p').text.split(",")
        sz=addr[-1].strip().split(" ")
        del addr[-1]
        zips.append(sz[1])
        states.append(sz[0])
        cities.append(addr[-1])
        del addr[-1]
        street.append(",".join(addr))
        lat.append(li.get('data-lat'))
        long.append(li.get('data-lng'))
        locs.append(li.find('h2').text)
        ph = li.find('a').text.strip()
        if ph == "":
            ph = "<MISSING>"
        phones.append(ph)
        page_url.append(li.find('div', {'class': 'actions'}).find_all('a')[3].get('href'))
        id=re.findall(r'location=(.*)',li.find('div', {'class': 'actions'}).find_all('a')[0].get('href'))
        if id==[]:
            id="<MISSING>"
        else:
            id=id[0]
        ids.append(id)

    for url in page_url:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')

        tim=soup.find_all('div', {'class': 'box-content'})

        if tim==[]:
            timing.append("<MISSING>")
            continue
        tim=tim[0]
        tim=tim.find_all('dd')[2].text.replace("\n"," ").strip()
        if tim=="":
            tim="<MISSING>"
        print (tim)
        timing.append(tim)

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.donatos.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append("https://www.donatos.com/locations/all")  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

