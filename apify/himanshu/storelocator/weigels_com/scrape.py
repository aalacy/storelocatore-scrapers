import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('weigels_com')

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    #import certifi # This should be already installed as a dependency of 'requests'
    import warnings
    from requests.packages.urllib3.exceptions import InsecureRequestWarning

    warnings.simplefilter('ignore',InsecureRequestWarning)
    base_url = "https://weigels.com"
    r = session.get(base_url+"/location/",verify =False)
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find('div',{"class":"location-list"}).find_all('div',{'class':"location"})
    for loc in main:
        lat=loc['data-lat']
        zip="<MISSING>"
        lng=loc['data-lng']
        name=loc.find('div',{"class":"locationInfo"}).find('h4').text.strip()
        storeno=loc.find('div',{"class":"locationInfo"}).find('h4').text.strip().split(' ')[-1]
        hour=' '.join(list(loc.find('div',{"class":"locationInfo"}).find('div',{'class':"locationHours"}).stripped_strings)).replace('Hours:','').strip()
        madd=loc.find('div',{"class":"locationInfo"}).find('div',{'class':"locationAddress"}).text.strip().split(',')
        if "United States" in " ".join(madd):
            madd.remove(" United States")

        if len(madd) == 4:
            zipp_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str("".join(madd[1:])))
            if zipp_list:
                zipp = zipp_list[0].strip()
            else:
                zipp = "<MISSING>"
            street_address = madd[0].strip()
            city = madd[1].strip()
            state_list = re.findall(r' ([A-Z]{2}) ', str(" ".join(madd[-2:])))
            if state_list:
                state = state_list[-1].strip()
            else:
                state = madd[-1].strip()

        elif len(madd) == 3:
            zipp_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str("".join(madd[1:])))
            if zipp_list:
                zipp = zipp_list[0].strip()
            else:
                zipp = "<MISSING>"
            state = madd[-1].strip().split()[0]
            city = madd[-2].strip()
            street_address= madd[0].strip()
        elif len(madd) == 2:
            zipp_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str("".join(madd[1:])))
            if zipp_list:
                zipp = zipp_list[0].strip()
            else:
                zipp = "<MISSING>"
            state = madd[-1].strip().split()[0]
            city = madd[0].split()[-1].strip()
            street_address = " ".join(madd[0].split()[:-1]).strip()


        else:
            zipp_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str("".join(madd)))
            if zipp_list:
                zipp = zipp_list[0].strip()
            else:
                zipp = "<MISSING>"
            street_address =" ".join(madd[0].split()[:-1]).strip()
            if madd[0].split()[-1].isdigit():
                city= "<MISSING>"
            else:
                city = madd[0].split()[-1].strip()






        phone=loc.find('div',{"class":"locationInfo"}).find('div',{'class':"locationPhone"}).text.strip()
        store=[]
        store.append(base_url)
        store.append(name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(storeno)
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        if hour.strip():
            store.append(hour.strip())
        else:
            store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(base_url+"/location/")
        for i in range(len(store)):
            if type(store[i]) == str:
                store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        store = [x if x else "<MISSING>" for x in store]
        return_main_object.append(store)
        # logger.info("data =="+str(store))
        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
