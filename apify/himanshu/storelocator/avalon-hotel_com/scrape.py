import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.avalon-hotel.com/"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    store_listing = soup.find("li",{"id": "menu-item-1347"}).find('ul')
    alla = store_listing.find_all('li')
    for i in range(len(alla)):
        store_no=alla[i]['id'].split('-')[-1]
        link=alla[i].find('a')['href']
        r1 = session.get(link)
        soup1 = BeautifulSoup(r1.text,"lxml")
        link1 = soup1.find("ul",{"class":"topnav-menu"}).find('li').find("ul",{"class":"sub-menu"}).find('a')['href']
        r2 = session.get(link1)
        soup2 = BeautifulSoup(r2.text,"lxml")
        store_name=soup2.find("h2",{"class":"feattitlebox-subtitle"}).text.strip()
        mainaddress=soup2.find('div',{'class':"ftr-address left"}).text.split(",")
        mlat=soup2.find('div',{'class':"ftr-address left"}).find('a')['href'].split('@')[-1]
        lat=mlat.split(',')[0]
        lng=mlat.split(',')[1]
        state=mainaddress[-1].split(' ')[-2].strip()
        zip=mainaddress[-1].split(' ')[-1].strip()
        phone = soup2.find('div',{'class':"ftr-phone left"}).find('span').text
        if len(mainaddress) == 3:
            address=mainaddress[-3]
            city=mainaddress[-2]
        else:
            address1=mainaddress[-2].split(' ')
            city =address1[-2]+" "+address1[-1]
            address =mainaddress[-2].split(city)[0]
        store = []
        store.append("https://www.avalon-hotel.com")
        store.append(store_name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append("US")
        store.append(store_no)
        try:
            store.append(phone)
        except:
            store.append("<MISSING>")
        store.append("Avalon Hotel")
        try:
            store.append(lat)
            store.append(lng)
        except:
            store.append("<MISSING>")
            store.append("<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
