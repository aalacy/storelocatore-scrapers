import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline= '') as output_file:
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
    addressess = []
    base_url = "http://samssoutherneatery.com"
    r = session.get(
        "https://www.ordersamssoutherneatery.com/locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    # for a in soup.find("main", {"class": "Index"}).find_all("a"):
    for link in soup.find_all(lambda tag: (tag.name == "a") and "Order Now" in tag.text):
        page_url = link['href']
        if "/locations-list" not in page_url:
            r_loc = session.get(page_url, headers=headers)
            soup_loc = BeautifulSoup(r_loc.text, 'lxml')
            locator_domain = base_url
            jd = str(soup_loc).split("<script>")[1].split("</script>")[0]
            location_name = jd.split('var _locationName = "')[1].split('";')[0]
            addr = jd.split('var _locationAddress = "')[1].split('";')[0].split(",")
            if len(addr)==4:
                street_address = " ".join(addr[:2]).replace(" Springhill","").strip()
                city = addr[2].strip()
                state = addr[3].strip().split(" ")[0]
                zipp = addr[3].strip().split(" ")[1]
            else:
                street_address = addr[0].lower().strip()
                city = addr[1].lower().strip()
                state = addr[2].strip().split(" ")[0]
                zipp = addr[2].strip().split(" ")[1]

            store_number = jd.split('var _locationId = "')[1].split('";')[0]
            phone = soup_loc.find(lambda tag: (tag.name == "a") and "(" in tag.text).text
            latitude = jd.split('var _locationLat = ')[1].split(';')[0]
            longitude = jd.split('var _locationLng = ')[1].split(';')[0]
            hour_page = page_url+"/Website/Hours"
            hour_r = session.get(hour_page, headers=headers)
            hour_soup = BeautifulSoup(hour_r.text, 'lxml')
            hours_of_operation = " ".join(list(hour_soup.stripped_strings)[1:]).replace("Business Hours","Business Hours :").replace("Carryout Hours",",Carryout Hours :")

            store = []
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zipp if zipp else '<MISSING>')
            store.append('US')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append("Sam's Southern Eatery")
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(hours_of_operation if hours_of_operation else '<MISSING>')
            store.append(page_url)
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            yield store
    
    
    rm_link = [
            "https://www.samssouthernpinebluff.com",
            "https://www.samssouthernwhitehall.com",
            "https://www.samssouthernnatchitoches.com",
            "https://www.samssouthernmarlow.com",
            "https://www.samssoutherntahlequah.com",
            "https://www.samssouthernbethany.com",
            "https://www.samssouthernlawton.com"
            ]

    for rm in rm_link:
        if rm =="https://www.samssouthernpinebluff.com":
            location_name = "Sam's Southern Eatery Pine Bluff"
            street_address = "1704 E Harding Ave"
            city = "Pine Bluff"
            state = "AR"
            zipp = "71601"
            phone = "(870) 536-2222"
        if rm =="https://www.samssouthernwhitehall.com":
            location_name = "Sam's Southern Eatery White Hall"
            street_address = "7003 Dollarway Rd"
            city = "White Hall"
            state = "AR"
            zipp = "71602"
            phone = "(870) 395-7433"
        if rm =="https://www.samssouthernnatchitoches.com":
            location_name = "Sam's Southern Eatery Natchitoches"
            street_address = "303 South Dr"
            city = "Natchitoches"
            state = "LA"
            zipp = "71457"
            phone = "(318) 352-6213"
        if rm =="https://www.samssouthernmarlow.com":
            location_name = "Sam's Southern Eatery Marlow"
            street_address = "1011 S Broadway St"
            city = "Marlow"
            state = "OK"
            zipp = "73055"
            phone = "(580) 721-7070"
        if rm =="https://www.samssoutherntahlequah.com":
            location_name = "Sam's Southern Eatery Tahlequah"
            street_address = "1721 S Muskogee Ave"
            city = "Tahlequah"
            state = "OK"
            zipp = "74464"
            phone = "(918) 772-5099"
        if rm =="https://www.samssouthernbethany.com":
            location_name = "Sam's Southern Eatery Bethany"
            street_address = "7000 NW 23rd St7000 NW 23rd St"
            city = "Bethany"
            state = "OK"
            zipp = "73008"
            phone = "(405) 730-6017"
        if rm =="https://www.samssouthernlawton.com":
            location_name = "Sam's Southern Eatery Lawton"
            street_address = "801 SW 11th St"
            city = "Lawton"
            state = "OK"
            zipp = "73505"
            phone = "(580) 713-5455"
        store_number = '<MISSING>'
        latitude = '<MISSING>'
        longitude = '<MISSING>'
        hours_of_operation = '<MISSING>'
        page_url = '<MISSING>'


        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append('US')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append("Sam's Southern Eatery")
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url if page_url else '<MISSING>')
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
        

    r1 = session.get("https://samssoutherneatery.com/locations-list", headers=headers)
    soup1 = BeautifulSoup(r1.text, "lxml")
    for link in soup1.find_all(lambda tag: (tag.name == "a") and "Order Now" in tag.text):
        page_url = link['href'].replace("/#/","")

        if "/locations-list" not in page_url:
           
            if page_url in rm_link:
                continue

            r_loc = session.get(page_url, headers=headers)
            soup_loc = BeautifulSoup(r_loc.text, 'lxml')
            locator_domain = base_url
            jd = str(soup_loc).split("<script>")[1].split("</script>")[0]
            location_name = jd.split('var _locationName = "')[1].split('";')[0]
            addr = jd.split('var _locationAddress = "')[1].split('";')[0].split(",")
            if len(addr)==4:
                street_address = " ".join(addr[:2]).replace(" Springhill","").strip()
                city = addr[2].strip()
                state = addr[3].strip().split(" ")[0]
                zipp = addr[3].strip().split(" ")[1]
            else:
                street_address = addr[0].lower().strip()
                city = addr[1].lower().strip()
                state = addr[2].strip().split(" ")[0]
                zipp = addr[2].strip().split(" ")[1]

            store_number = jd.split('var _locationId = "')[1].split('";')[0]
            phone = soup_loc.find(lambda tag: (tag.name == "a") and "(" in tag.text).text
            latitude = jd.split('var _locationLat = ')[1].split(';')[0]
            longitude = jd.split('var _locationLng = ')[1].split(';')[0]
            hour_page = page_url+"/Website/Hours"
            hour_r = session.get(hour_page, headers=headers)
            hour_soup = BeautifulSoup(hour_r.text, 'lxml')
            hours_of_operation = " ".join(list(hour_soup.stripped_strings)[1:]).replace("Business Hours","Business Hours :").replace("Carryout Hours",",Carryout Hours :")
            if page_url =="https://www.samssoutherntoledo.com":
                location_name = "Sam's Southern Eatery Toledo"
                hours_of_operation = "Business Hours Mon - Sat:	9:00 AM - 9:00 PM Sun:	11:00 AM - 9:00 PM, Carryout Hours Mon - Sat:	9:00 AM - 8:45 PM Sun:	11:00 AM - 8:45 PM"

            store = []
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zipp if zipp else '<MISSING>')
            store.append('US')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append("Sam's Southern Eatery")
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(hours_of_operation if hours_of_operation else '<MISSING>')
            store.append(page_url if page_url else '<MISSING>')
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
