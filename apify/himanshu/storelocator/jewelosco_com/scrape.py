import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import urllib3
import html5lib
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('local.jewelosco')
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url= "https://local.jewelosco.com/index.html"

    headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,pt;q=0.8',
    'cache-control': 'max-age=0',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
    }
    
   
    r = session.get("https://local.jewelosco.com/index.html", headers=headers, verify=False)

    soup = BeautifulSoup(r.text, "html5lib")
    
    for link in soup.find_all("a",{"class":"Directory-listLink"}):
        if link['data-count'] != "(1)":
            city = "https://local.jewelosco.com/"+link['href']
            r1 = session.get(city, headers=headers)
            soup1 = BeautifulSoup(r1.text, "html5lib")
            for dt in soup1.find_all("a",{"class":"Directory-listLink"}):
                if dt['data-count'] != "(1)":
                    page_url = "https://local.jewelosco.com/"+dt['href']
                    r2 = session.get(page_url, headers=headers)
                    soup2 = BeautifulSoup(r2.text, "html5lib")
                    for dt1 in soup2.find_all("a",{"class":"Teaser-titleLink"}):
                        main_page_url ="https://local.jewelosco.com"+ dt1['href'].replace("..","")
                        address_data = session.get(main_page_url, headers=headers)
                        soup_address = BeautifulSoup(address_data.text, "html5lib")
                        add_val = soup_address.find_all("span",{"class":"c-address-street-1"})
                        add_val_city = soup_address.find_all("span",{"class":"c-address-city"})
                        add_val_state = soup_address.find_all("abbr",{"class":"c-address-state"})
                        add_val_postal = soup_address.find_all("span",{"class":"c-address-postal-code"})
                        store_phone = soup_address.find_all("div",{"class":"Phone-display Phone-display--withLink"})
                        
                        store_name = soup_address.find_all("span",{"aria-current":"page"})
                        location_name = soup_address.find_all("h1",{"class":"ContentBanner-h1"})

                        location_type = soup_address.find_all("span",{"class":"c-bread-crumbs-name"})
                        latitude = soup_address.find_all("meta",{"itemprop":"latitude"})[0]['content']
                        longitude = soup_address.find_all("meta",{"itemprop":"longitude"})[0]['content']
                        
                        
                        time = soup_address.find("table",{"class":"c-hours-details"}).text.strip().replace("Day of the WeekHours",'').replace("Monday","Monday ").replace("AM","AM ").replace("PM","PM ").replace("Sunday","Sunday ")
                       
                        street_address = add_val[0].text.strip()
                        city = add_val_city[0].text.strip()
                        state = add_val_state[0].text.strip()
                        postal = add_val_postal[0].text.strip()
                        country = "US"
                        phone = store_phone[0].text.strip()
                        location = location_type[0].text.strip()
                        store_number_val = store_name[0].text.strip()
                        location_name_val = location_name[0].text.strip()


                        store = []
                        store.append(base_url)
                        store.append(location_name_val)
                        store.append(street_address)
                        store.append(city)
                        store.append(state)
                        store.append(postal)
                        store.append(country)
                        store.append("<MISSING>")
                        store.append(phone if phone else "<MISSING>")
                        store.append("<MISSING>")
                        store.append(latitude if latitude else "<MISSING>")
                        store.append(longitude if longitude else "<MISSING>")
                        store.append(time)
                        store.append(main_page_url)
                        # logger.info("data =="+str(store))
                        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                        yield store

                else:
                    single_page_url = "https://local.jewelosco.com/"+dt['href']
                    address_data2 = session.get(single_page_url, headers=headers)
                    soup_address2 = BeautifulSoup(address_data2.text, "html5lib")
                    add_val = soup_address2.find_all("span",{"class":"c-address-street-1"})
                    add_val_city = soup_address2.find_all("span",{"class":"c-address-city"})
                    add_val_state = soup_address2.find_all("abbr",{"class":"c-address-state"})
                    add_val_postal = soup_address2.find_all("span",{"class":"c-address-postal-code"})
                    store_phone = soup_address2.find_all("div",{"class":"Phone-display Phone-display--withLink"})
                    
                    store_name = soup_address2.find_all("span",{"aria-current":"page"})
                    location_name = soup_address2.find_all("h1",{"class":"ContentBanner-h1"})

                    location_type = soup_address2.find_all("span",{"class":"c-bread-crumbs-name"})
                    latitude = soup_address2.find_all("meta",{"itemprop":"latitude"})[0]['content']
                    longitude = soup_address2.find_all("meta",{"itemprop":"longitude"})[0]['content']
                    
                    
                    time = soup_address2.find("table",{"class":"c-hours-details"}).text.strip().replace("Day of the WeekHours",'').replace("Monday","Monday ").replace("AM","AM ").replace("PM","PM ").replace("Sunday","Sunday ")
                    
                    street_address = add_val[0].text.strip()
                    city = add_val_city[0].text.strip()
                    state = add_val_state[0].text.strip()
                    postal = add_val_postal[0].text.strip()
                    country = "US"
                    phone = store_phone[0].text.strip()
                    location = location_type[0].text.strip()
                    store_number_val = store_name[0].text.strip()
                    location_name_val = location_name[0].text.strip()


                    store = []
                    store.append(base_url)
                    store.append(location_name_val)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(postal)
                    store.append(country)
                    store.append("<MISSING>")
                    store.append(phone if phone else "<MISSING>")
                    store.append("<MISSING>")
                    store.append(latitude if latitude else "<MISSING>")
                    store.append(longitude if longitude else "<MISSING>")
                    store.append(time)
                    store.append(single_page_url)
                    # logger.info("data =="+str(store))
                    # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    yield store
                  
        else:
            single_city = "https://local.jewelosco.com/"+link['href'] 
            address_data3 = session.get(single_page_url, headers=headers)
            soup_address3 = BeautifulSoup(address_data3.text, "html5lib")
            add_val = soup_address3.find_all("span",{"class":"c-address-street-1"})
            add_val_city = soup_address3.find_all("span",{"class":"c-address-city"})
            add_val_state = soup_address3.find_all("abbr",{"class":"c-address-state"})
            add_val_postal = soup_address3.find_all("span",{"class":"c-address-postal-code"})
            store_phone = soup_address3.find_all("div",{"class":"Phone-display Phone-display--withLink"})
            
            store_name = soup_address3.find_all("span",{"aria-current":"page"})
            location_name = soup_address3.find_all("h1",{"class":"ContentBanner-h1"})

            location_type = soup_address3.find_all("span",{"class":"c-bread-crumbs-name"})
            latitude = soup_address3.find_all("meta",{"itemprop":"latitude"})[0]['content']
            longitude = soup_address3.find_all("meta",{"itemprop":"longitude"})[0]['content']
            
            
            time = soup_address3.find("table",{"class":"c-hours-details"}).text.strip().replace("Day of the WeekHours",'').replace("Monday","Monday ").replace("AM","AM ").replace("PM","PM ").replace("Sunday","Sunday ")
            
            street_address = add_val[0].text.strip()
            city = add_val_city[0].text.strip()
            state = add_val_state[0].text.strip()
            postal = add_val_postal[0].text.strip()
            country = "US"
            phone = store_phone[0].text.strip()
            location = location_type[0].text.strip()
            store_number_val = store_name[0].text.strip()
            location_name_val = location_name[0].text.strip()


            store = []
            store.append(base_url)
            store.append(location_name_val)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(postal)
            store.append(country)
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(time)
            store.append(single_city)
            # logger.info("data =="+str(store))
            # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store
       
                
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
