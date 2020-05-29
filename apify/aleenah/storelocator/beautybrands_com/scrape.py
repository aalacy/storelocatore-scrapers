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

    res=requests.get("https://www.beautybrands.com/store-locator/all-stores.do")
    soup = BeautifulSoup(res.text, 'html.parser')
    sa = soup.find_all('div', {'class': 'eslStore ml-storelocator-headertext'})

    for a in sa:
        a=a.find('a')
        url="https://www.beautybrands.com/"+a.get('href')
        print(url)
        page_url.append(url)
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        locs.append(soup.find('div', {'class': 'eslStore'}).text)
        street.append(soup.find('div', {'class': 'eslAddress1'}).text+" "+soup.find('div', {'class': 'eslAddress2'}).text)
        cities.append(soup.find('span', {'class': 'eslCity'}).text.replace(",",""))
        states.append(soup.find('span', {'class': 'eslStateCode'}).text.strip())
        zips.append(soup.find('span', {'class': 'eslPostalCode'}).text)
        ph=soup.find('div', {'class': 'eslPhone'}).text.strip()
        if ph=="":
            ph="<MISSING>"
        phones.append(ph)
        tim=soup.find('span', {'class': 'ml-storelocator-hours-details'}).text.replace("Book Appointment","").replace("Call","").strip()
        if tim=="":
            tim="<MISSING>"
        timing.append(tim.replace("Sunday"," Sunday"))
        strsoup=str(soup)
        lat.append(re.findall(r'"latitude":(-?[\d\.]+)',strsoup)[0])
        long.append(re.findall(r'"longitude":(-?[\d\.]+)',strsoup)[0])
        ids.append(re.findall(r'"code":"([\d]+)","address"',strsoup)[0])

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.beautybrands.com/")
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
        row.append(page_url[i])  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
