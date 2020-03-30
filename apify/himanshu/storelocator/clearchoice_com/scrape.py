import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
 


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # zips = sgzip.coords_for_radius(50)
    # zips = sgzip.for_radius(100)
    return_main_object = []




    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Accept": "application/json, text/plain, */*",
        # "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    base_url = "https://www.clearchoice.com/"
    locator_domain = "https://www.clearchoice.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "clearchoice"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    r = session.get('https://www.clearchoice.com/locations/',headers = headers)
    soup = BeautifulSoup(r.text,"lxml")
    for item in soup.find_all('div',class_="item-list")[1:]:
        for a in item.find_all('a'):
            r_loc = session.get(a['href'],headers = headers)
            soup_loc = BeautifulSoup(r_loc.text,"lxml")
            page_url = a['href']
            latitude = soup_loc.find('meta',{'itemprop':'latitude'})['content']
            longitude = soup_loc.find('meta',{'itemprop':'longitude'})['content']
            location_name = soup_loc.find('div',class_="contact").find('h2').text
            address = soup_loc.find('div',class_="location-address")
            list_address = list(address.stripped_strings)
            if len(list_address) == 6:
                street_address = " ".join(list_address[:2])
                city = "".join(list_address[2])
                state = "".join(list_address[-2])
                 
                zipp = "".join(list_address[-1])
            else:
                street_address = "".join(list_address[0])
                city = "".join(list_address[1])
                state = "".join(list_address[-2])
                zipp = "".join(list_address[-1])
            phone = soup_loc.find('span',{'itemprop':'telephone'}).text.strip()
            if(state == 'Washington'):
                    state='WA'
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
            store = [x if x else "<MISSING>" for x in store]

            # print("data = " + str(store))
            # print(
            #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
