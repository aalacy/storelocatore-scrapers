import csv
from sgrequests import SgRequests
import json
# from datetime import datetime
# import phonenumbers
from bs4 import BeautifulSoup
import re
# import unicodedata
# import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('good-sam_com')




session = SgRequests()

def write_output(data):
    with open('data.csv',newline="", mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = "https://www.good-sam.com/"
    addresses = []
    temp = []
    country_code = "US"
    location_type = "<MISSING>"
    hours_of_operation = "<MISSING>"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    r = session.get("https://www.good-sam.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    
    for links in  soup.find("map",{"id":"usa"}).find_all("area"):
        link = "https://www.good-sam.com/locations"+links["href"]
        r1 = session.get(link,headers=headers)
        soup1 = BeautifulSoup(r1.text,"lxml")
        loc = json.loads(soup1.find("div",class_="location-google-map")["data-locations"])
        for x in loc:
            store_number = x["entry_id"]
            location_name = x["title"]
            # logger.info(location_name)
            latitude = x["latitude"]
            longitude = x["longitude"]
            state = x["location_state"]
            city = x["location_city"]
            phone = x["location_phone"]
            page_url ="https://www.good-sam.com"+ x["url"]
            r2 = session.get(page_url,headers=headers)
            soup2 = BeautifulSoup(r2.text,"lxml")
            
            try:
                address =" ".join(list(soup2.find("div",class_="page-header-meta").find("address").stripped_strings)).split(",")
                street_address = " ".join(address[:-2]).strip()

                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(address[-1]))
                if us_zip_list:
                    zipp=us_zip_list[0]
                else:
                    zipp="<MISSING>"
                if street_address:
                    street_address = street_address
                    # logger.info(street_address)
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                                store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

                    store = [str(x).strip() if x else "<MISSING>" for x in store]
                    # logger.info(street_address)
                    # logger.info("data = " + str(store))
                    # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    temp.append(store)
                else:
                    if soup2.find("div",class_="accordion"):
                        for div in soup2.find_all("div",class_="accordion"):
                            for p in div.find_all("p"):
                                page_url = p.find("a")["href"]
                                if "http" in a:
                                    page_url = page_url
                                else:
                                    page_url = "https://www.good-sam.com"+page_url

                                r = session.get(page_url,headers=headers)
                                soup = BeautifulSoup(r.text,"lxml")
                                location_name = soup.find("div",class_="page-header-meta").find("h1").text.strip()
                                address =" ".join(list(soup.find("div",class_="page-header-meta").find("address").stripped_strings)).split(",")
                                street_address = " ".join(address[:-2]).strip()
                                city = address[-2]
                                state = address[-1].split()[0]
                                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(address[-1]))
                                if us_zip_list:
                                    zipp=us_zip_list[0]
                                else:
                                    zipp="<MISSING>"
                                phone_tag = soup.find("a",class_="phone").text.strip()
                                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))
                                if phone_list:
                                    phone = phone_list[0]
                                else:
                                    phone = "<MISSING>"
                                latitude = latitude
                                longitude = longitude
                                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                                store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

                                store = [str(x).strip() if x else "<MISSING>" for x in store]
                                # logger.info(street_address)
                                # logger.info("data = " + str(store))
                                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                                temp.append(store)   
                    else:
                        for div in soup2.find("div",class_="article-text").find_all("p"):
                            try:
                                a = div.find("a")["href"]
                                if "http" in a:
                                    page_url = a
                                else:
                                    page_url = "https://www.good-sam.com"+a
                                r = session.get(page_url,headers=headers)
                                soup = BeautifulSoup(r.text,"lxml")
                                location_name = soup.find("div",class_="page-header-meta").find("h1").text.strip()
                                address =" ".join(list(soup.find("div",class_="page-header-meta").find("address").stripped_strings)).split(",")
                                street_address = " ".join(address[:-2]).strip()
                                city = address[-2]
                                state = address[-1].split()[0]
                                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(address[-1]))
                                if us_zip_list:
                                    zipp=us_zip_list[0]
                                else:
                                    zipp="<MISSING>"
                                phone_tag = soup.find("a",class_="phone").text.strip()
                                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))
                                if phone_list:
                                    phone = phone_list[0]
                                else:
                                    phone = "<MISSING>"
                                latitude = latitude
                                longitude = longitude
                                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                                store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

                                store = [str(x).strip() if x else "<MISSING>" for x in store]
                                # logger.info(street_address)
                                # logger.info("data = " + str(store))
                                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                                temp.append(store)

                            except:
                                pass
 


                            
            except Exception as e:
                street_address = "<MISSING>"
                zipp = "<MISSING>"
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                                store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

                store = [str(x).strip() if x else "<MISSING>" for x in store]
                # logger.info(street_address)
                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                temp.append(store)
            

                
    for i in range(len(temp)):
        if "hawaii-home" in temp[i][-1]:
            temp[i][-6] = "(808) 235-6314" 
        if (temp[i][-1]) in addresses:
            continue
        addresses.append(temp[i][-1])
        yield temp[i]
        # logger.info(temp[i])

def scrape():
    data = fetch_data()
    write_output(data)

scrape()



# if "Serving the communities of Brainerd and Pine River" in city:
#     city = "Pine River"
# if  "Providing senior care and services in Greeley" in city:
#     city = "Greeley"
# if "Serving the communities of Prescott and Prescott Valley" in city :
#     city = "Prescott Valley"
# if "Serving the community of Luverne" in city:
#     city = "Luverne"
# if "Serving Hastings" in city:
#     city = "Hastings"
# if "Serving the community of Albion" in city:
#     city = "Albion"
# if "Serving the community of Valentine" in city:
#     city = "Valentine"
# if "Providing senior care and services in and around Sioux Falls" in city:
#     city="Sioux Falls"



# list of url where street_address,zip are missing on web :

# https://www.good-sam.com/locations/miller-pointe
# https://www.good-sam.com/locations/sunset-drive
# https://www.good-sam.com/locations/marillac-manor
# https://www.good-sam.com/locations/st-vincents

# added all missing location excepting above page_url
