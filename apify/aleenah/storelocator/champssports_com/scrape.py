import csv
import re
from bs4 import BeautifulSoup
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('champssports_com')



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
    countries=[]

    res=requests.get("https://stores.champssports.com/")
    soup = BeautifulSoup(res.text, 'html.parser')
    uls = soup.find('div', {'class': 'Directory-content'}).find_all("ul")
    usa = uls[0].find_all('a')+uls[2].find_all('a')+uls[3].find_all('a')
    can=uls[1].find_all('a')

    for a in usa:
        #logger.info("usa")
        if a.get('data-count') == "(1)":
            #logger.info(url)
            page_url.append("https://stores.champssports.com/"+a.get('href').replace("../",""))
            countries.append('US')
        else:

            url = "https://stores.champssports.com/"+a.get('href').replace("../","")
            #logger.info(url)
            res=requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            sa = soup.find('div', {'class': 'Directory-content'}).find_all("a")

            for d in sa:
                if d.get('data-count') == "(1)":
                    if "https://stores.champssports.com/" +d.get("href").replace("../","") not in page_url:
                        page_url.append("https://stores.champssports.com/" +d.get("href").replace("../",""))
                        countries.append('US')
                else:
                    url = "https://stores.champssports.com/" + d.get('href').replace("../","")
                    #logger.info(url)
                    res = requests.get(url)
                    soup = BeautifulSoup(res.text, 'html.parser')
                    sas = soup.find_all('a', {'class': 'Teaser-titleLink'})
                    for s in sas:
                        if "https://stores.champssports.com/"+s.get("href").replace("../","") not in page_url:
                            page_url.append("https://stores.champssports.com/"+s.get("href").replace("../",""))
                            countries.append('US')

    for a in can:
        if a.get('data-count') == "(1)":
            page_url.append("https://stores.champssports.com/"+a.get('href').replace("../",""))
            countries.append('CA')
            #logger.info(url)
        else:

            url = "https://stores.champssports.com/"+a.get('href')
            #logger.info(url)
            res=requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            sa = soup.find('div', {'class': 'Directory-content'}).find_all("a")

            for d in sa:
                if d.get('data-count') == "(1)":
                    page_url.append("https://stores.champssports.com/" +d.get("href").replace("../",""))
                    countries.append('CA')
                else:
                    url = "https://stores.champssports.com/" + d.get('href').replace("../","")
                    #logger.info(url)
                    res = requests.get(url)
                    soup = BeautifulSoup(res.text, 'html.parser')
                    sas = soup.find_all('a', {'class': 'Teaser-titleLink'})
                    for s in sas:
                        if "https://stores.champssports.com/"+s.get("href").replace("../","") not in page_url:
                           page_url.append("https://stores.champssports.com/"+s.get("href").replace("../",""))
                           countries.append('CA')

    #page_url=set(page_url)
    logger.info(len(page_url))

    key_set=set([])
    k=0
    for url in page_url:
        logger.info(url)
        #if k==1:
         #      del page_url[page_url.index(url)-1]
        #k=0
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        div = soup.find('div', {'class': 'Core-row l-row'})

        c=div.find('span', {'class': 'c-address-city'}).text
        s=div.find_all('abbr',{'class':'c-address-state'})
        if s != []:
             s=s[0].text
        else:
             s= "<MISSING>"
        st=div.find('span', {'class': 'c-address-street-1'}).text
        z=div.find('span', {'class': 'c-address-postal-code'}).text
        if s+c+z+st in key_set:
          logger.info("This is a duplicate, but its data is added to the file")
          """street.append("<MISSING>") 
          locs.append("<MISSING>")
          street.append("<MISSING>")
          cities.append("<MISSING>")
          states.append("<MISSING>")
          zips.append("<MISSING>")
          phones.append("<MISSING>")
          timing.append(tim.strip().strip(',') )
          lat.append(re.findall(r'(-?[\d\.]+);',latlng)[0])
          long.append(re.findall(r';(-?[\d\.]+)',latlng)[0])
          #del countries[page_url.index(url)]
          #k=1
          continue"""
        key_set.add(s+c+z+st)
        locs.append(soup.find('span',{'class':'LocationName-geo'}).text)
        street.append(st)
        cities.append(c)
        states.append(s)
        zips.append(z)
        phones.append(div.find('div', {'id': 'phone-main'}).text)
        tim=""
        tims=div.find('tbody').find_all('tr')
        for t in tims:
            tim+= t.get('content')+", "
        timing.append(tim.strip().strip(',').replace("Mo","Monday").replace("Tu","Tuesday").replace("We","Wednesday").replace("Th","Thursday").replace("Fr","Friday").replace("Sa","Saturday").replace("Su","Sunday") )

        latlng=soup.find_all('meta')[17].get('content')
        #logger.info(latlng)
        lat.append(re.findall(r'(-?[\d\.]+);',latlng)[0])
        long.append(re.findall(r';(-?[\d\.]+)',latlng)[0])

    all = []
    for i in range(0, len(locs)):
        row = []
        #if street[i]=="<MISSING>":
        #  continue
        row.append("https://stores.champssports.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append(countries[i])
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)
        #logger.info(row)

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
