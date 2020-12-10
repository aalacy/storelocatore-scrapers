import csv
import time
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('searshomeservices_com')


session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    addresses = []
    base_url = "https://www.searshomeservices.com"
    addresses = []
   
    r = session.get("https://www.searshomeservices.com/locations/", headers=headers)
    
    soup= BeautifulSoup(r.text,"lxml")
    links = soup.find_all('a', class_='state')

    for link in links:
        
        r1 = session.get(base_url+link['href'], headers=headers)
        
        soup1 = BeautifulSoup(r1.text, "lxml")
        loc_links = soup1.find_all('a', class_='see-more')

        for loc_link in loc_links:

            if "http" not in loc_link['href']:
                page_url = base_url+loc_link['href']
               
                r4 = session.get(page_url, headers=headers)
                       
                soup4 = BeautifulSoup(r4.text, "lxml")
                json_str = (soup4.text.split("config.currentStore = ")[1]+"{").split("}]};")[0]+"}]}"
                json_data = json.loads(json_str)
                street_address = str(json_data["address"])
                location_name = str(json_data["location_name"])
                city = str(json_data["city"])
                state = str(json_data["state"])
                zipp = str(json_data["zip"])
                phone = str(json_data["phone"])
                store_number = str(json_data["id"])
                latitude = str(json_data["lat"])
                longitude = str(json_data["long"])
                location_type = str(json_data["location_type"])

                ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp))
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp))

                country_code = ""
                if ca_zip_list:
                    zipp = ca_zip_list[-1]
                    country_code = "CA"
            
                if us_zip_list:
                    zipp = us_zip_list[-1]
                    country_code = "US"

            else:
                page_url = loc_link['href'].lower()
                # logger.info(page_url)

                r3 = session.get(page_url, headers=headers)
            
                soup3 = BeautifulSoup(r3.text, "lxml")
                head= soup3.find('div',class_='headerMain-utilZone03')

                if head != None:                    
                    city = head.find('span',{'itemprop':'addressLocality'}).text.strip()
                    state = head.find('span',{'itemprop':'addressRegion'}).text.strip()
                    phone = head.find('nav',{'class':'navCallout'}).find('a')['href'].replace('tel:','').strip()
                    # logger.info(phone)
                    location_name = city
                    street_address = "<MISSING>"
                    zipp = "<MISSING>"
                    location_type = "<MISSING>"
                    store_number = "<MISSING>"
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                    hours_of_operation = "<MISSING>"
                    country_code = "US"
                    page_url = page_url

                else:
                    if soup3.find("label",{"id":"currentUrl"}) != None:
                        city = soup3.find("label",{"id":"currentUrl"}).text.split(',')[0].strip()
                        state = soup3.find("label",{"id":"currentUrl"}).text.split(',')[1].strip()
                        phone = soup3.find("div", {"itemprop":"telephone"}).text
                        # logger.info(phone)
                        location_name = city
                        info = soup3.find("div", {"class":"subcontainer rightside"})
                        if info != None:
                            if info.find("div", {"itemprop":"streetAddress"}):
                                street_address = info.find("div", {"itemprop":"streetAddress"}).text.strip()
                            else:
                                street_address = "<MISSING>"
                            if info.find("span", {"itemprop":"postalCode"}):
                                zipp = info.find("span", {"itemprop":"postalCode"}).text.strip()
                            else:
                                zipp = "<MISSING>"
                        else:
                            street_address = "<MISSING>"
                            zipp = "<MISSING>"
                        location_type = "<MISSING>"
                        store_number = "<MISSING>"
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                        hours_of_operation = "<MISSING>"
                        country_code = "US"
                        page_url = page_url
                    else:
                        #page not found
                        pass

           
            loc_r = session.get(page_url, headers=headers)
            

            loc_soup = BeautifulSoup(loc_r.text, "lxml")

            if loc_soup.find("span",{"class":"store-hours"}):
            
                hours_of_operation = " ".join(list(loc_soup.find("span",{"class":"store-hours"}).stripped_strings)).replace('Hours','').strip()
            else:
                hours_of_operation = "<MISSING>"
        
                
               
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number) 
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            # logger.info("data ==== "+str(store))
            # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
