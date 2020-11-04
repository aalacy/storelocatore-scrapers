import json
import time
import csv
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests

session = SgRequests()

def write_output(data):
    with open('subway_com1.csv', mode='w',newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    addressess = []
    base_url= "https://restaurants.subway.com/united-states"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    k = soup.find_all("a",{"class":"Directory-listLink","href":re.compile("united-states/")})
    for i in k[:26]:
        state_url = "https://restaurants.subway.com/"+i['href']
        try:
            r1 = session.get(state_url)
        except:
            continue
        soup1 = BeautifulSoup(r1.text,'lxml')
        city_data = soup1.find_all("a",{"class":"Directory-listLink"})
        for j in city_data:
            if j['data-count']=="(1)":
                page_url = j['href'].replace("..","https://restaurants.subway.com/")
                # print(page_url)
                try:
                    r2 = session.get(page_url)
                except:
                    continue
                soup2 = BeautifulSoup(r2.text,'lxml')
                jd = json.loads(str(soup2).split('"entities": ')[1].split(', "nearbyLocs":')[0])[0]
                location_name = soup2.find("h1",{"itemprop":"name"}).text.replace("Subway","Subway at").replace("  "," ").strip()
                # location_name = jd['altTagText']
                street_address = jd['profile']['address']['line1']
                city = jd['profile']['address']['city']
                state = jd['profile']['address']['region']
                zipp = jd['profile']['address']['postalCode']
                try:
                    store_number = jd['profile']['c_franchiseNum']
                except:
                    store_number = "<MISSING>"
                try:
                    phone = jd['profile']['mainPhone']['display']
                except:
                    phone = "<MISSING>"
                location_type = "Subway Restaurant"
                latitude = jd['profile']['yextDisplayCoordinate']['lat']
                longitude = jd['profile']['yextDisplayCoordinate']['long']
                hours_of_operation = " ".join(list(soup2.find("table",{"class":"c-hours-details"}).stripped_strings)).replace("Day of the Week Hours","")
                
                store=[]
                store.append("https://www.subway.com/")
                store.append(location_name if location_name else "<MISSING>")
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append("US")
                store.append(store_number)
                store.append(phone if phone else "<MISSING>")
                store.append(location_type)
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hours_of_operation if hours_of_operation.strip() else "<MISSING>")
                store.append(page_url)
                store = [x.replace("–","-") if type(x) == str else x for x in store]
                store = [x.strip() if type(x) == str else x for x in store]
                if store[2] in addressess:
                    continue
                addressess.append(store[2])
                yield store
            else:
                city_link = j['href'].replace("..","https://restaurants.subway.com/")
                try:
                    city_r = session.get(city_link)
                except:
                    continue
                city_soup = BeautifulSoup(city_r.text,'lxml')
                for i in city_soup.find_all("a",{"class":"Teaser-title"}):
                    page_url = i['href'].replace("../../","https://restaurants.subway.com/")
                    try:
                        r2 = session.get(page_url)
                    except:
                        continue
                    soup2 = BeautifulSoup(r2.text,'lxml')
                    jd = json.loads(str(soup2).split('"entities": ')[1].split(', "nearbyLocs":')[0])[0]
                    location_name = soup2.find("h1",{"itemprop":"name"}).text.replace("Subway","Subway at").replace("  "," ").strip()
                    # location_name = jd['altTagText']
                    street_address = jd['profile']['address']['line1']
                    city = jd['profile']['address']['city']
                    state = jd['profile']['address']['region']
                    zipp = jd['profile']['address']['postalCode']
                    try:
                        store_number = jd['profile']['c_franchiseNum']
                    except:
                        store_number = "<MISSING>"
                    try:
                        phone = jd['profile']['mainPhone']['display']
                    except:
                        phone = "<MISSING>"
                    location_type = "Subway Restaurant"
                    latitude = jd['profile']['yextDisplayCoordinate']['lat']
                    longitude = jd['profile']['yextDisplayCoordinate']['long']
                    try:
                        hours_of_operation = " ".join(list(soup2.find("table",{"class":"c-hours-details"}).stripped_strings)).replace("Day of the Week Hours","")
                    except AttributeError:
                        hours_of_operation = "<MISSING>"

                    store=[]
                    store.append("https://www.subway.com/")
                    store.append(location_name if location_name else "<MISSING>")
                    store.append(street_address if street_address else "<MISSING>")
                    store.append(city if city else "<MISSING>")
                    store.append(state if state else "<MISSING>")
                    store.append(zipp if zipp else "<MISSING>")
                    store.append("US")
                    store.append(store_number)
                    store.append(phone if phone else "<MISSING>")
                    store.append(location_type)
                    store.append(latitude if latitude else "<MISSING>")
                    store.append(longitude if longitude else "<MISSING>")
                    store.append(hours_of_operation if hours_of_operation.strip() else "<MISSING>")
                    store.append(page_url)
                    store = [x.replace("–","-") if type(x) == str else x for x in store]
                    store = [x.strip() if type(x) == str else x for x in store]
                    if store[2] in addressess:
                        continue
                    addressess.append(store[2])
                    yield store

#==========================================================================================================
    time.sleep(20)
    for i in k[26:-1]:
        state_url = "https://restaurants.subway.com/"+i['href']
        try:
            r1 = session.get(state_url)
        except:
            continue
        soup1 = BeautifulSoup(r1.text,'lxml')
        city_data = soup1.find_all("a",{"class":"Directory-listLink"})
        for j in city_data:
            if j['data-count']=="(1)":
                page_url = j['href'].replace("..","https://restaurants.subway.com/")
                try:
                    r2 = session.get(page_url)
                except:
                    continue
                soup2 = BeautifulSoup(r2.text,'lxml')
                location_name = soup2.find("h1",{"itemprop":"name"}).text.replace("Subway","Subway at").replace("  "," ")
                jd = json.loads(str(soup2).split('"entities": ')[1].split(', "nearbyLocs":')[0])[0]
                # location_name = jd['altTagText']
                street_address = jd['profile']['address']['line1']
                city = jd['profile']['address']['city']
                state = jd['profile']['address']['region']
                zipp = jd['profile']['address']['postalCode']
                try:
                    store_number = jd['profile']['c_franchiseNum']
                except:
                    store_number = "<MISSING>"
                try:
                    phone = jd['profile']['mainPhone']['display']
                except:
                    phone = "<MISSING>"
                location_type = "Subway Restaurant"
                latitude = jd['profile']['yextDisplayCoordinate']['lat']
                longitude = jd['profile']['yextDisplayCoordinate']['long']
                hours_of_operation = " ".join(list(soup2.find("table",{"class":"c-hours-details"}).stripped_strings)).replace("Day of the Week Hours","")
                
                store=[]
                store.append("https://www.subway.com/")
                store.append(location_name if location_name else "<MISSING>")
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append("US")
                store.append(store_number)
                store.append(phone if phone else "<MISSING>")
                store.append(location_type)
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hours_of_operation if hours_of_operation.strip() else "<MISSING>")
                store.append(page_url)
                store = [x.replace("–","-") if type(x) == str else x for x in store]
                store = [x.strip() if type(x) == str else x for x in store]
                if store[2] in addressess:
                    continue
                addressess.append(store[2])
                yield store
            else:
                city_link = j['href'].replace("..","https://restaurants.subway.com/")
                try:
                    city_r = session.get(city_link)
                except:
                    continue
                city_soup = BeautifulSoup(city_r.text,'lxml')
                for i in city_soup.find_all("a",{"class":"Teaser-title"}):
                    page_url = i['href'].replace("../../","https://restaurants.subway.com/")
                    try:
                        r2 = session.get(page_url)
                    except:
                        continue
                    soup2 = BeautifulSoup(r2.text,'lxml')
                    location_name = soup2.find("h1",{"itemprop":"name"}).text.replace("Subway","Subway at").replace("  "," ")
                    jd = json.loads(str(soup2).split('"entities": ')[1].split(', "nearbyLocs":')[0])[0]
                    # location_name = jd['altTagText']
                    street_address = jd['profile']['address']['line1']
                    city = jd['profile']['address']['city']
                    state = jd['profile']['address']['region']
                    zipp = jd['profile']['address']['postalCode']
                    try:
                        store_number = jd['profile']['c_franchiseNum']
                    except:
                        store_number = "<MISSING>"
                    try:
                        phone = jd['profile']['mainPhone']['display']
                    except:
                        phone = "<MISSING>"
                    location_type = "Subway Restaurant"
                    latitude = jd['profile']['yextDisplayCoordinate']['lat']
                    longitude = jd['profile']['yextDisplayCoordinate']['long']
                    try:
                        hours_of_operation = " ".join(list(soup2.find("table",{"class":"c-hours-details"}).stripped_strings)).replace("Day of the Week Hours","")
                    except AttributeError:
                        hours_of_operation = "<MISSING>"

                    store=[]
                    store.append("https://www.subway.com/")
                    store.append(location_name if location_name else "<MISSING>")
                    store.append(street_address if street_address else "<MISSING>")
                    store.append(city if city else "<MISSING>")
                    store.append(state if state else "<MISSING>")
                    store.append(zipp if zipp else "<MISSING>")
                    store.append("US")
                    store.append(store_number)
                    store.append(phone if phone else "<MISSING>")
                    store.append(location_type)
                    store.append(latitude if latitude else "<MISSING>")
                    store.append(longitude if longitude else "<MISSING>")
                    store.append(hours_of_operation if hours_of_operation.strip() else "<MISSING>")
                    store.append(page_url)
                    store = [x.replace("–","-") if type(x) == str else x for x in store]
                    store = [x.strip() if type(x) == str else x for x in store]
                    if store[2] in addressess:
                        continue
                    addressess.append(store[2])
                    yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()




