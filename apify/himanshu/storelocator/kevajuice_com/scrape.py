import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline="",encoding="utf-8") as output_file:
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
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    base_url = "http://kevajuice.com/"

    addresses = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = "<MISSING>"
    phone = ""
    location_type = "<MISSING>"
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    page_url = ""

    r= session.get("http://www.kevajuicesw.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for loc in soup.find_all("div",class_="x-content-band man"):
        for loc1 in loc.find_all("div",class_="one-third"):
            try:
                page_url = "http://www.kevajuicesw.com/locations/"
                location_name = loc1.find("p",class_="stores").text.strip()
                store_number = location_name.split("#")[1].split()[0]
                address = list(loc1.find("p",class_="stores").find_next("p").stripped_strings)
                if "(Near Food Court)" in address[0]:
                    del address[0]
                # print(address)
                street_address = address[0].strip()
                if "201 Third St. NW" == street_address:
                    street_address = street_address + " " + "Suite D"
                if len(address) > 1:
                    city  = address[1].split(",")[-2].strip()
                    
                    state = address[1].split(",")[-1].split()[0].strip()
                    us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(address[1].split(",")[-1]))
                    if us_zip_list:
                        zipp =us_zip_list[0]
                    else:
                        zipp = "<MISSING>"

                    phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(address[-1]))
                    if phone_list:
                        phone = phone_list[0]
                        if ")" in phone:
                            phone ="("+phone_list[0] 
                    else:
                        phone =  list(loc1.find("p",class_="stores").find_next("p").find_next("p").stripped_strings)[0]
                        
                    
                else:
                    city="<MISSING>"
                    state = "<MISSING>"
                    zipp = "<MISSING>"
                    phone= "<MISSING>"
                hours_of_operation = " ".join(list(loc1.find_all("p")[-1].stripped_strings)).replace("Hours","").replace("(Drive Thru Only)","")
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                store = ["<MISSING>" if x == "" else x for x in store]
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                
                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store
                
            except:
                pass

    list_store_url = []
    r = session.get("http://kevajuice.com/store-locator/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for script in soup.find_all("div", {'class': re.compile('tp-caption')}):
        list_store_url.append(script.find('a')['href'])
        list_store_url = list(dict.fromkeys(list_store_url))

    for store_url in list_store_url:
        if "nevada" not in store_url and "new-mexico" not in store_url:
            # print(store_url)
            r_store = session.get(store_url, headers=headers)
            soup_store = BeautifulSoup(r_store.text, "lxml")
            table = soup_store.find('table')
            # print(table)
            for tr in table.find_all('tr')[1:]:
                page_url = store_url
                if 'http://kevajuice.com/colorado/'in page_url:
                    page_url = 'http://www.kevajuicecolorado.com/index2.html'
                address = list(tr.find_all('td')[0].stripped_strings)
                # print(address)
                # print('~~~~~~~~~~~~~~')
                if address == []:
                    location_name = "<MISSING>"
                    street_address = "<MISSING>"
                    city = "<MISSING>"
                    state = "<MISSING>"
                    zipp = "<MISSING>"
                elif len(address) == 1:
                    location_name = address[0].strip()
                    street_address = "<MISSING>"
                    city = "<MISSING>"
                    state = "<MISSING>"
                    zipp = "<MISSING>"
                elif len(address) == 2:
                    street_address = address[0].strip()
                    location_name = address[1].replace(
                        "Located in the", "").strip()
                    city = "<MISSING>"
                    state = "<MISSING>"
                    zipp = "<MISSING>"

                else:
                    location_name = address[0].strip()
                    street_address = " ".join(address[1:-1]).strip()
                    city = address[-1].split(',')[0].strip()
                    state = address[-1].split(',')[-1].split()[0].strip()
                    zipp = address[-1].split(',')[-1].split()[-1].strip()
                if "Lubbock Keva" == location_name.strip():
                    page_url = "https://www.kevajuicelubbock.com/"
                if "http://kevajuice.com/utah/" == page_url:
                    page_url = "https://www.kevajuiceutah.com/"
                hours_of_operation = " ".join(
                    list(tr.find_all('td')[1].stripped_strings)).strip().replace("Follows Airport Hours", "").replace("Follows Mall Hours ", "").replace("May vary", "").strip()
                phone_list = list(tr.find_all('td')[2].stripped_strings)
                if "Store Website" in " ".join(phone_list):
                    phone_list.remove("Store Website")
                if phone_list:
                    phone = phone_list[0]
                else:
                    phone = "<MISSING>"

                try:
                    coord = tr.find_all('td')[3].a['href']

                    if "&sll" in coord:
                        latitude = coord.split("&sll=")[1].split(',')[0]
                        longitude = coord.split("&sll=")[1].split(',')[
                            1].split('&')[0]
                    else:

                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                except:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                store = ["<MISSING>" if x == "" else x for x in store]
                store = [str(x).encode('ascii', 'ignore').decode(
                    'ascii').strip() if x else "<MISSING>" for x in store]

                if (store[1] + " " + store[2]) in addresses:
                    continue
                addresses.append(store[1] + " " + store[2])
                # print("data = " + str(store))
                # print(
                #    '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
