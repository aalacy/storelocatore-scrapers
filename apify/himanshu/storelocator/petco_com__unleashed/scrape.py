import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('petco_com__unleashed')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://stores.petco.com"
    r = session.get(base_url,headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    store_name = []
    store_detail = []
    return_main_object = []
    addresss = []
    link = (soup.find_all("a", {"class": "gaq-link", "data-gaq": "List, Region"}))
    # logger.info(link)
    # logger.info(len(link))
    # exit()

    
    for index, i in enumerate(link):
        r1 = session.get(i['href'])
        soup1 = BeautifulSoup(r1.text, "lxml")
        link1 = soup1.find_all("a", {"class": "gaq-link", "data-gaq": "List, City"})
        
        for j in link1:
            
            r2 = session.get(j['href'], headers=headers)
            soup2 = BeautifulSoup(r2.text, "lxml")
            details = soup2.find_all(
                "a", {"class": "btn btn-primary store-info gaq-link"})
            for q in details:
                tem_var = [] 
                page_url = q['href']
                # logger.info(page_url)
                r3 = session.get(q['href'], headers=headers)
                soup3 = BeautifulSoup(r3.text, "html5lib")
                json1 = json.loads(soup3.find(
                    "script", {"type": "application/ld+json"}).text)
                # logger.info(json1)
            #     # logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++")
                if "Unleashed" in soup3.find("span", class_="location-name").text.strip():

                    location_name = soup3.find("span", class_="location-name").text.strip()
                    store_number = soup3.find("span", class_="store-number").text.replace("Store:", "").strip()
                    # logger.info(location_name)
                    # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    # logger.info("============================link", details)
                
                    hours = " ".join(list(soup3.find("div", {"class": "hours"}).stripped_strings))
                    latitude = json1[0]['geo']['latitude']
                    longitude = json1[0]['geo']['longitude']
                    name = json1[0]['mainEntityOfPage']['breadcrumb']['itemListElement'][0]['item']['name']
                    # logger.info(json1[0]['address'])
                    phone = json1[0]['address']['telephone']
                    st = json1[0]['address']['streetAddress']
                    city = json1[0]['address']['addressLocality']
                    state = json1[0]['address']['addressRegion']
                    zip1 = json1[0]['address']['postalCode']

                    tem_var.append("https://stores.petco.com")
                    tem_var.append(location_name)
                    tem_var.append(st)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zip1)
                    tem_var.append("US")
                    tem_var.append(store_number)
                    tem_var.append(phone)
                    tem_var.append("PetStore")
                    tem_var.append(latitude)
                    tem_var.append(longitude)
                    tem_var.append(hours)
                    tem_var.append(page_url)
                    if tem_var[2] in addresss:
                        continue
                    addresss.append(tem_var[2])

                    # logger.info("==", str(tem_var))
                    # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    yield tem_var


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
