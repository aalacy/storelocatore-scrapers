import csv
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup
import re



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
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
    base_url = "https://www.zipscarwash.com"
    page = 0
    while page<=8:

        r = session.get('https://www.zipscarwash.com/search-by-state?field_address_administrative_area=All&page='+str(page) , headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        page_url = []
        latitude = []
        longitude = []
        hours = []
        location_name = []
        phone = []
        address = soup.find_all("div", {"class":"views-field views-field-field-address"})
        link = soup.find_all("div",{"class":"views-field views-field-title"})
        direction = soup.find_all("div",{"class":"views-field views-field-field-regional-manager"})
        time = soup.find_all("span",{"class":"office-hours__item-slots"})
        contact = soup.find_all("div", {"class":"views-field views-field-field-location-hours"})
        for number in contact:
            if number.parent.find("div",{"class":"views-field views-field-field-phone-no"}) != None:
                phone.append(number.parent.find("div",{"class":"views-field views-field-field-phone-no"}).text.replace("Phone:","").strip())
            else:
                phone.append("<MISSING>")
        for hour in time:
            hours.append("Sunday"+" "+str(hour.text)\
            +" "+"Monday"+" "+str(hour.text)\
            +" "+"Tuesday"+" "+str(hour.text)\
            +" "+"Wednesday"+" "+str(hour.text)\
            +" "+"Thursday"+" "+str(hour.text)\
            +" "+"Friday"+" "+str(hour.text)\
            +" "+"Saturday"+" "+str(hour.text))
        for cord in direction:
            
            if cord.find("div",{"class":"home-page-direction"}) != None:
                try:
                    latitude.append(cord.find("div",{"class":"home-page-direction"}).find("a")['href'].split("=")[1].split("&")[0])
                    longitude.append(cord.find("div",{"class":"home-page-direction"}).find("a")['href'].split("=")[-1])
                except:
                    latitude.append("<MISSING>")
                    longitude.append("<MISSING>")
            else:
                latitude.append("<MISSING>")
                longitude.append("<MISSING>")
            

        for direct in link:
            page_url.append("https://www.zipscarwash.com"+direct.find("a")['href'])
            location_name.append(direct.find("a").text.split("(")[0])
            
        for index,i in enumerate(address):
            name = location_name[index]
            street_address = i.find("span",{"class":"address-line1"}).text
            city = i.find("span",{"class":"locality"}).text
            state = i.find("span",{"class":"administrative-area"}).text
            zipp = i.find("span",{"class":"postal-code"}).text
            store_number = page_url[index].split("/")[-1]

            store = []
            store.append(base_url)
            store.append(name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append(store_number)
            store.append(phone[index])
            store.append("<MISSING>")
            store.append(latitude[index])
            store.append(longitude[index])
            store.append(hours[index])
            store.append(page_url[index])
            yield store
        page+=1

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
