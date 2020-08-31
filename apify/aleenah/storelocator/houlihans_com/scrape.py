import csv
import re
from bs4 import BeautifulSoup
import requests

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states = []
    cities = []
    types = []
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids = []
    page_url = []
    urls=[]
    res = requests.get("https://houlihans.com/find-a-location")
    soup = BeautifulSoup(res.text, 'html.parser')
    lis = soup.find('div', {'class': 'sf_cols'}).find_all('a')
    print(len(lis))

    for li in lis:

        u = li.get('href')
        print(u)
        if "www.houlihans.com" not in u:
            if "//bit.ly" not in u:
                urls.append("https://houlihans.com" + u)
                locs.append(li.text)
        else:
            locs.append(li.text)
            urls.append(u)

    for url in urls:
        #print(url)
        try:
            res = requests.get(url)
        except:
            del locs[urls.index(url)]
            continue
        page_url.append(url)

        soup = BeautifulSoup(res.text, 'html.parser')
        street.append(soup.find('span', {'class': 'd_address1'}).text.strip())
        cities.append(soup.find('span', {'class': 'd_city'}).text.strip())
        states.append(soup.find('span', {'class': 'd_state'}).text.strip())
        zips.append(soup.find('span', {'class': 'd_zip'}).text.strip())
        ph = soup.find('span', {'class': 'd_phone'}).text.strip()
        if ph != "":
            phones.append(ph)
        else:
            phones.append("<MISSING>")



        tim=re.sub(r'[ ]+',' ',soup.find('span', {'class': 'd_hours'}).prettify().replace('&amp;','-').replace('<span class="d_hours">','').replace('</span>','').replace('<br/>','').replace('\n\n','\n').replace('\n',' ').strip())
        timing.append(tim)
        try:
            coord = soup.find('a', {'id': 'MainContent_hlDirections'}).get('href')
            lat.append(re.findall(r'q=(-?[\d\.]*)', coord)[0])
            long.append(re.findall(r'q=[-?\d\.]*\,([-?\d\.]*)', coord)[0])
        except:
            lat.append('<MISSING>')
            long.append('<MISSING>')
        try:
            ids.append(soup.find('input', {'id': 'hidStoreNumber'}).get('value'))
        except:
            ids.append('<MISSING>')

        try:
            types.append(re.findall(r'<div itemscope="" itemtype="http://schema\.org/([^"]*)">', str(soup), re.DOTALL)[0])
        except:
            types.append('<MISSING>')

        """locs.append(soup.find('span', {'itemprop': 'name'}).text)
    strees = soup.find_all('span', {'itemprop': 'streetAddress'})
    st = ""
    for stree in strees:
        st += stree.text
    street.append(st)
    cities.append(soup.find('span', {'itemprop': 'addressLocality'}).text)
    states.append(soup.find('span', {'itemprop': 'addressRegion'}).text)
    zips.append(soup.find('span', {'itemprop': 'postalCode'}).text)
    ph = soup.find('span', {'itemprop': 'telephone'}).text.strip()
    if ph != "":
        phones.append(ph)
    else:
        phones.append("<MISSING>")

    tim = soup.find('div', {'class': 'location-hours pod half'}).text.strip()
    if tim != "":
        timing.append(tim.replace('\r\n', " ").replace('\n', " ").replace('\t', ""))
    else:
        timing.append("<MISSING>")
    coord = soup.find('a', {'id': 'MainContent_hlDirections'}).get('href')
    lat.append(re.findall(r'q=(-?[\d\.]*)', coord)[0])
    long.append(re.findall(r'q=[-?\d\.]*\,([-?\d\.]*)', coord)[0])
    ids.append(soup.find('input', {'id': 'hidStoreNumber'}).get('value'))
    #print(soup)
    types.append(re.findall(r'<div itemscope="" itemtype="http://schema\.org/([^"]*)">',str(soup),re.DOTALL)[0])"""


    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://houlihans.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append(types[i])  # type
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
