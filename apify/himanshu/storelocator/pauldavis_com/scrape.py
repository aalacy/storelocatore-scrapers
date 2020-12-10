import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import certifi # This should be already installed as a dependency of 'requests'
import warnings
from urllib3.exceptions import InsecureRequestWarning
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('pauldavis_com')


session = SgRequests()
def write_output(data):
    with open('data.csv', 'w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # logger.info("data::" + str(data))
        for i in data or []:
            writer.writerow(i)
def fetch_data():  
    addresses = []
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'content-type': "application/x-www-form-urlencoded",
            'accept': "application/json, text/javascript, */*; q=0.01",
            'cache-control': "no-cache",
        }
    base_url = "https://www.pauldavis.com"
    # canada location
    r = session.get('https://pauldavis.ca/wp-json/locator/v1/list/?formattedAddress=&boundsNorthEast=&boundsSouthWest=',headers = headers).json()

    for loc in r:
        location_name = loc['name']
        if "fr-Paul Davis Location" in location_name:
            continue

        street_address = loc['address'].replace(",","").replace("Hanwell N.B. E3E 2E7","").strip()
        city = loc['city']
        state = loc['state']
        zipp = loc['postal']
        latitude = loc['lat']
        longitude = loc['lng']
        phone = loc['phone']
        page_url = loc['web']
        country_code = "CA"
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append("<MISSING>") 
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append("<MISSING>")
        store.append(page_url)
        store = [x.strip() if x else "<MISSING>" for x in store]
        
        yield store

    # us location
    warnings.simplefilter('ignore',InsecureRequestWarning)
    links = []
    us_r = session.get("https://pauldavis.com/paul-davis-locations/", verify=False)
    soup1 = BeautifulSoup(us_r.text, "lxml")
    state_data = soup1.find_all('div', class_='cell tablet-4')

    for link in state_data:
        city_href = base_url + link.find("a")['href']
        # try:
        city_r = session.get(city_href, verify=False)
        # except:
        #     continue
        city_soup = BeautifulSoup(city_r.text, "lxml")
        city_data = city_soup.find('main', class_="main small-12 tablet-9 cell")
       
        for loc in city_data.find_all("div"):
            loc_href= base_url + loc.a['href']
            # try:
            loc_r = session.get(loc_href, verify=False)
            # except:
            #     continue
            loc_soup = BeautifulSoup(loc_r.text, "lxml")
            url = loc_soup.find('main', class_="main small-12 tablet-9 cell").find("div").a['href']
            if "https:" in url:
                page_url = url
            elif "http:" in url:
                page_url = url
            else:
                page_url = "https://" + url
            #logger.info("Page url is",page_url)
            if page_url == "https://pauldavis.com":
                continue
            if page_url in links:
                continue
            links.append(page_url)     
            
            # try:
            data_r = session.get(page_url, verify=False)
            # except:
            #     continue
            data_soup = BeautifulSoup(data_r.text, "lxml")
            phone_list = re.findall(re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(data_soup.find("span",{"class":"phone-icon"}).text.strip()))
            if phone_list:
                phone = phone_list[0]
            else:
                phone = "<MISSING>"
            try:
                location_name = re.sub(r'\s+'," ",data_soup.find("span",{"itemprop":"name"}).text)
                street_address = data_soup.find("span",{"itemprop":"streetAddress"}).text
                city =  data_soup.find("span",{"itemprop":"addressLocality"}).text
                state = data_soup.find("span",{"itemprop":"addressRegion"}).text
                zipp = data_soup.find("span",{"itemprop":"postalCode"}).text
                # phone = data_soup.find("span",{"itemprop":"telephone"}).text
                coord = session.get(data_soup.find("link",{"itemprop":"hasMap"})['href']).url
                latitude = coord.split("@")[1].split(",")[0]
                longitude = coord.split("@")[1].split(",")[1]

            except:
                if len(data_soup.find_all('p',class_='info')) == 4:
                    street_address = data_soup.find_all('p',class_='info')[1].text
                    city = data_soup.find_all('p',class_='info')[2].text.split(',')[0]
                    state = data_soup.find_all('p',class_='info')[2].text.split(',')[1].split(' ')[1].replace('.','')
                    zipp = data_soup.find_all('p',class_='info')[2].text.split(',')[1].split(' ')[2]
                    # phone = data_soup.find_all('p',class_='info')[0].text
                elif len(data_soup.find_all('p',class_='info')) == 5:
                    street_address = data_soup.find_all('p',class_='info')[2].text
                    city = data_soup.find_all('p',class_='info')[3].text.split(',')[0]
                    state = data_soup.find_all('p',class_='info')[3].text.split(',')[1].split(' ')[1].replace('.','')
                    zipp = data_soup.find_all('p',class_='info')[3].text.split(',')[1].split(' ')[2]
                    # phone = data_soup.find_all('p',class_='info')[0].text
                else:
                    # phone = data_soup.find_all('p',class_='info')[0].text
                    street_address = data_soup.find_all('p',class_='info')[1].text
                    city = data_soup.find_all('p',class_='info')[2].text.split(",")[0]
                    state = data_soup.find_all('p',class_='info')[2].text.split(",")[1].replace(".","").split()[0]
                    zipp = data_soup.find_all('p',class_='info')[2].text.split(",")[1].replace(".","").split()[1]
                
                
  
                location_name = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            country_code = "US"
            
        
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address.replace(",","").strip())
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append("<MISSING>") 
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append("<MISSING>")
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            store = [x.strip() if x else "<MISSING>" for x in store]
            # logger.info(store)
            yield store

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
