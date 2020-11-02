import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('seniorhelpers_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    
        # logger.info("zip_code === "+zip_code)
    locator_domain = "https://www.seniorhelpers.com/"
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
    location_url = "https://www.seniorhelpers.com/our-offices"
    
    # data="------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"zip\"\r\n\r\n"+str(zip_code)+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--" 
    
    # try:
    r = requests.get(location_url,headers=headers)
    # except:
    #     pass
    soup = BeautifulSoup(r.text, "html5lib")
    for ut in soup.find("section",{"class":"offices-list"}).find("div",{"class":"col-12"}).find_all("li"):
        for ut1 in (ut.find_all("a")):
            page_url="https://www.seniorhelpers.com"+ut1['href']
            hours_of_operation=''
            r1 = requests.get(page_url,headers=headers)
            soup1 = BeautifulSoup(r1.text, "html5lib")
            # phone = soup1.find("a",{"class":"swappable-number swappable-number-mobile"}).text.strip()
            try:
                phone  = soup1.find(lambda tag: (tag.name == "span") and "Contact" == tag.text.strip()).parent.parent.text.strip().replace("Contact",'').strip().lstrip()
            except:
                phone="<MISSING>"
            # logger.info(phone)
            try:
                hours_of_operation  = " ".join(list(soup1.find(lambda tag: (tag.name == "span") and "Hours" == tag.text.strip()).parent.parent.stripped_strings)).replace("Hours",'')
            except:
                hours_of_operation="<MISSING>"
            location_name = ut1.text.strip()
            full  = list(soup1.find(lambda tag: (tag.name == "span") and "Address" == tag.text.strip()).parent.parent.stripped_strings)
            for index,delq in enumerate(full):
                if full[index][:7]=="License" or full[index][:6]== "Office" or full[index][:3]=="HHA":
                    del full[index]
            if full[-1] =="Directions"  :
                del full[-1]
            if full[0] =="Address"  :
                del full[0]
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(full[-1]))
            if us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"
            state_list = re.findall(r' ([A-Z]{2})', str(full[-1]))
            if state_list:
                state = state_list[-1]
            city = full[-1].split(",")[0]
            street_address=(" ".join(full[:-1]))

            latitude = "<MISSING>"
            longitude = "<MISSING>"
            store_number="<MISSING>"
            location_type="<MISSING>"
            
            
            store = ["https://www.seniorhelpers.com", location_name, street_address.encode('ascii', 'ignore').decode('ascii').strip(), city, state, zipp, country_code,
                        store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            # if store[2] in addresses:
            #     continue
            # addresses.append(store[2])
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store
        
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
