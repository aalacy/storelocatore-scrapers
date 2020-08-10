import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.townfairtire.com"
    # print(base_url+'/store/tires/connecticut/branford/')
    r = session.get('https://www.townfairtire.com/store/tires/')
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    addressess=[]
    output=[]
    main=soup.find('div',{'class':"storeLocations"}).find_all('a')
    # print(len(main))
    # exit()
    for atag in main:
        # if len(atag['href'].split('/'))>5:

            # print(base_url+atag['href'])
        if "Connecticut Stores:" in  atag.text or "Massachusetts Stores:" in  atag.text or "Rhode Island Stores:" in atag.text or "New Hampshire Stores:" in atag.text or "Maine Stores:" in atag.text or "Vermont Stores:" in atag.text:
            continue
        # print("----")
        page_url = base_url+atag['href']

        r1 = session.get(base_url+atag['href'])
        soup1=BeautifulSoup(r1.text,'lxml')
        latitude = (json.loads(soup1.find("script",{"type":"application/ld+json"}).text)['geo']['latitude'])
        longitude = (json.loads(soup1.find("script",{"type":"application/ld+json"}).text)['geo']['longitude'])

        main1=list(soup1.find('div',{'class':"storeInfo"}).stripped_strings)
        address=main1[0].strip()
        ct=main1[1].strip().split(',')
        city=ct[0].strip()
        state=ct[1].strip().split(' ')[0].strip()
        zip=ct[1].strip().split(' ')[1].strip()
        phone=soup1.find('div',{"id":"ContentPlaceHolder1_UpdatePanel2"}).find("button").text.strip()
        hour=list(soup1.find('div',{"class":"storeHours"}).stripped_strings)
        del hour[0]
        hour=' '.join(hour)
        country="US"
        lat=''
        lng=''
        name=soup1.find('div',{"class":"tireBrand"}).find('h1').text.strip()
        store=[]
        store.append(base_url)
        store.append(name if name else "<MISSING>")
        store.append(address if address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zip if zip else "<MISSING>")
        store.append(country if country else "<MISSING>")
        store.append("<MISSING>")
        store.append(phone.replace("Call ",'') if phone else "<MISSING>")
        store.append("townfairtire")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")
        # if store[2] in addressess:
        #     continue
        # addressess.append(store[2])
        yield store

            # if zip not in output:
            #     output.append(zip)
            #     return_main_object.append(store)
    # return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
