import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import html5lib
session = SgRequests()

gd_soup = BeautifulSoup(session.get("https://www.lifecareservices-seniorliving.com/find-a-community/").text, "html5lib")
 
gd_nonce = gd_soup.find(lambda tag : (tag.name == "script") and "nonce" in tag.text).text.split("nonce: '")[1].split("'")[0]

def write_output(data):
    with open('data.csv', mode='w',newline='\n') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    # locator_domain = "https://www.lifecareservices-seniorliving.com/"
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""
    r2 = session.get("https://www.lifecareservices-seniorliving.com/",headers=headers)
    soup2 = BeautifulSoup(r2.text, "lxml")
    # gd_nonce = soup2.find(lambda tag: (tag.name == "script" ) and "var gd_ajax_vars" in tag.text.strip()).text.split("var gd_ajax_vars =")[-1].replace("};",'}').split("nonce:")[-1].split("url:")[0].replace("',",'').replace("'",'').strip()
    # print(gd_nonce)
    # exit()
    url = "https://www.lifecareservices-seniorliving.com/wp-admin/admin-ajax.php"

    data = {
            'pg': '1',
            'action': 'get_communities',
            'gd_nonce': str(gd_nonce)
        }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
  
    }

    response = session.post(url, headers=headers, data = data).json()
    for ut in response['results']:
        soup1 = BeautifulSoup(ut['html'], "html5lib")
        for data in soup1.find_all("div",{"class":"cmnty-results-address"}):
            full = list(data.find("p",{"class":"address"}).stripped_strings)
            if full[0]=="Information Center":
                del full[0]
            city = list(data.find("p",{"class":"address"}).stripped_strings)[-1].split(",")[0]
            state= list(data.find("p",{"class":"address"}).stripped_strings)[-1].split(",")[-1].strip().split(" ")[0]
            zipp = list(data.find("p",{"class":"address"}).stripped_strings)[-1].split(",")[-1].strip().split(" ")[-1]
            street_address = ' '.join(full[:-1])
            location_name=data.find("h5",{"class":"cmnty-results-item-heading"}).text.strip()
            if ", The" in location_name:
                location_name1 = location_name.split(",")[0]
                location_name = "The "+str(location_name1)
            phone = list(data.stripped_strings)[-2].replace("Chicago,       IL","<MISSING>").replace("Austin,       TX       78731","<MISSING>").replace("West Lafayette,       IN       47906-1431","<MISSING>").replace("Wheaton,       IL       60187","<MISSING>").replace("Bridgewater,       NJ       08807","<MISSING>").replace("Atchison,       KS       66002","<MISSING>").replace("Phoenix,       AZ       85018","(480) 573-3700")
            # print(phone)
            try:
                page_url =(data.find("h5",{"class":"cmnty-results-item-heading"}).find("a")['href'])
            except:
                page_url="<MISSING>"
            latitude = ut['latitude']
            # print(latitude)
            longitude = ut['longitude']
            store_number= ut['id']
            location_type="<MISSING>"
       
            hours_of_operation="<MISSING>"
            store = ["https://www.lifecareservices-seniorliving.com", location_name, street_address.encode('ascii', 'ignore').decode('ascii').strip(), city, state, zipp.replace("IL","<MISSING>"), country_code,
                        store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            # if store[2] in addresses:
            #     continue
            # addresses.append(store[2])
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store
        
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
