

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "updated_date", "hours_of_operation",'page_url'])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://www.homelessshelterdirectory.org/"
    url = []
    addressess = []

    soup = bs(session.get(base_url).content,"lxml")

    for s_link in soup.find_all("area",{"shape":"poly"}):
       
        state_soup = bs(session.get(s_link['href']).content, "lxml")

        for city_link in state_soup.find_all("a",{"title":re.compile("homeless shelters")}):

            city_soup = bs(session.get(city_link['href']).content, "lxml")
    
    
            for url in city_soup.find_all("a",{"class":"btn btn_red"}):
            
                page_url = url['href']
               # print(page_url)
                if page_url in url or "homelessshelterdirectory.org" not in page_url:
                    continue
                url.append(page_url)
                location_soup = bs(session.get(page_url).content, "lxml")
                try:
                    location_name = location_soup.find("h3",{"class":"entry_title"}).text
                except:
                    location_name = "<MISSING>"
                
                addr = list(location_soup.find("div",{"class":"col col_6_of_12"}).find("p").stripped_strings)
                if len(addr) > 2:
                    if re.sub(r'\s+',"",addr[1].replace(":","").replace("(","").replace(")","").replace("-","")).isdigit():
                        street_address = "<MISSING>"
                        city = city = addr[0].split(",")[0]
                        state = addr[0].split(",")[1].split()[0]
                        if len(addr[0].split(",")[1].split()) == 2:
                            zipp = addr[0].split(",")[1].split()[1]
                        else:
                            zipp = "<MISSING>"
                    
                        phone = addr[1].replace(":","").replace("_","").replace("?","").replace(",","").replace("24hrs","").strip()
                    else:

                        street_address = addr[0]
                        city = addr[1].split(",")[0]
                        state = addr[1].split(",")[1].split()[0]
                        if len(addr[1].split(",")[1].split()) == 2:
                            zipp = addr[1].split(",")[1].split()[1]
                        else:
                            zipp = "<MISSING>"
                        phone = addr[2].replace(":","").replace("_","").replace("?","").replace(",","").replace("24hrs","").strip()
                
                else:
                    street_address = "<MISSING>"
                    city = city = addr[0].split(",")[0]
                    state = addr[0].split(",")[1].split()[0]
                    if len(addr[0].split(",")[1].split()) == 2:
                        zipp = addr[0].split(",")[1].split()[1]
                    else:
                        zipp = "<MISSING>"
                
                    phone = addr[1].replace(":","").replace("_","").replace("?","").replace(",","").replace("24hrs","").strip()

                if "ext" in phone.lower():
                    phone = phone.lower().split("ext")[0].strip()
                if "or" in phone:
                    phone = phone.split("or")[0]
                store_number = page_url.split("=")[1]
            
                coords = location_soup.find(lambda tag:(tag.name == "script") and "setView" in tag.text).text.split("[")[1].split("]")[0]
                lat = coords.split(",")[0]
                lng = coords.split(",")[1].strip()
                if location_soup.find(lambda tag:(tag.name == "article") and "Shelter Information Last Update Date" in tag.text):
                    posted_date = location_soup.find(lambda tag:(tag.name == "article") and "Shelter Information Last Update Date" in tag.text).text
                    update_date = re.findall(r":\s+\d{4}-\d{2}-\d{2}",posted_date)[-1].replace(":","").strip()
                else:
                    update_date = "<MISSING>"
                

                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address.replace("?","").strip())
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append("US")
                store.append(store_number)
                store.append(phone.replace("x305","").replace("x 203","").strip())
                store.append("Shelter")
                store.append(lat)
                store.append(lng)
                store.append(update_date)
                store.append("<MISSING>")
                store.append(page_url)
                if store[2] in addressess:
                    continue
                addressess.append(store[2])
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                
                yield store



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
