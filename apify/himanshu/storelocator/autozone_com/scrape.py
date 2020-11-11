import csv
from bs4 import BeautifulSoup
import re
import json
import time
import platform
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('autozone_com')


session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    base_url = "https://www.autozone.com"
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
    }
    r = session.get("https://www.autozone.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    links = soup.find_all("li",{"class":"c-directory-list-content-item"})
    for link in links:
        state_link = "https://www.autozone.com/locations/"+(link.find("a")['href'])
        if link.find("span",{"class":"c-directory-list-content-item-count"}).text == "(1)":
            r1 = session.get(state_link, headers=headers)
            soup1 = BeautifulSoup(r1.text, "lxml")
            page_url = state_link
            # logger.info("page_url:111",page_url)
            street_address = soup1.find("span",{"class":"c-address-street-1"}).text.strip()
            state = soup1.find("abbr",{"class":"c-address-state"}).text
            zip1 = soup1.find("span",{"class":"c-address-postal-code"}).text
            city = soup1.find("span",{"class":"c-address-city"}).text
            name = " ".join(list(soup1.find("h1",{"class":"c-location-title"}).stripped_strings))
            # logger.info(name)
            try:
                store_number = (name.split("#")[1])
            except:
                store_number='<MISSING>'    
            phone = soup1.find("span",{"class":"c-phone-number-span c-phone-main-number-span"}).text
            hours = " ".join(list(soup1.find("table",{"class":"c-location-hours-details"}).find("tbody").stripped_strings))
            latitude = soup1.find("meta",{"itemprop":"latitude"})['content']
            longitude = soup1.find("meta",{"itemprop":"longitude"})['content']
            store1 =[]
            store1.append(base_url)
            store1.append(name)
            store1.append(street_address)
            store1.append(city)
            store1.append(state)
            store1.append(zip1)
            store1.append("US")
            store1.append(store_number)
            store1.append(phone)
            store1.append("<MISSING>")
            store1.append(latitude)
            store1.append(longitude)
            store1.append(hours)
            store1.append(page_url)
            store1 = [str(x).strip() if x else "<MISSING>" for x in store1]
            yield store1
            # logger.info("========================================",store1)
        else:
            r2 = session.get(state_link, headers=headers)
            soup2 = BeautifulSoup(r2.text, "lxml")
            for count in soup2.find_all("li",{"class":"c-directory-list-content-item"}):
                if count.find("span",{"class":"c-directory-list-content-item-count"}).text == "(1)":
                    page_url = "https://www.autozone.com/locations/"+count.find("a",{"class":"c-directory-list-content-item-link"})['href']
                    # logger.info("page_url:222",page_url)
                    r3 = session.get(page_url, headers=headers)
                    soup3 = BeautifulSoup(r3.text, "lxml")
                    street_address = soup3.find("span",{"class":"c-address-street-1"}).text.strip()
                    try:
                        state = soup3.find("abbr",{"class":"c-address-state"}).text
                    except:
                        state = "<MISSING>"
                    zip1 = soup3.find("span",{"class":"c-address-postal-code"}).text
                    city = soup3.find("span",{"class":"c-address-city"}).text
                    name = " ".join(list(soup3.find("h1",{"class":"c-location-title"}).stripped_strings))
                    # logger.info(name)
                    try:
                        store_number = (name.split("#")[1])
                    except:
                        store_number='<MISSING>'                        
                    phone = soup3.find("span",{"class":"c-phone-number-span c-phone-main-number-span"}).text
                    hours = " ".join(list(soup3.find("table",{"class":"c-location-hours-details"}).find("tbody").stripped_strings))
                    latitude = soup3.find("meta",{"itemprop":"latitude"})['content']
                    longitude = soup3.find("meta",{"itemprop":"longitude"})['content']
                    store2 =[]
                    store2.append(base_url)
                    store2.append(name)
                    store2.append(street_address)
                    store2.append(city)
                    store2.append(state)
                    store2.append(zip1)
                    store2.append("US")
                    store2.append(store_number)
                    store2.append(phone)
                    store2.append("<MISSING>")
                    store2.append(latitude)
                    store2.append(longitude)
                    store2.append(hours)
                    store2.append(page_url)
                    store2 = [str(x).strip() if x else "<MISSING>" for x in store2]
                    yield store2
                    # logger.info("========================================",store2)
                else:
                    r4 = session.get("https://www.autozone.com/locations/"+count.find("a",{"class":"c-directory-list-content-item-link"})['href'], headers=headers)
                    soup4 = BeautifulSoup(r4.text, "lxml")
                    for url in soup4.find_all("a",{"data-ya-track":"visitpage"}):
                        page_url = url['href'].replace('..','https://www.autozone.com/locations')
                        # logger.info("page_url:333",page_url)
                        r5 = session.get(page_url, headers=headers)
                        soup5 = BeautifulSoup(r5.text, "lxml")
                        try:
                            street_address = soup5.find("span",{"class":"c-address-street-1"}).text.strip()
                        except:
                            street_address=''
                        try:
                            state = soup5.find("abbr",{"class":"c-address-state"}).text
                        except:
                            state = "<MISSING>"
                        zip1 = soup5.find("span",{"class":"c-address-postal-code"}).text
                        city = soup5.find("span",{"class":"c-address-city"}).text
                        name = " ".join(list(soup5.find("h1",{"class":"c-location-title"}).stripped_strings))
                        # logger.info(name)
                        try:
                            store_number = (name.split("#")[1])
                        except:
                            store_number='<MISSING>'
                        phone = soup5.find("span",{"class":"c-phone-number-span c-phone-main-number-span"}).text
                        hours = " ".join(list(soup5.find("table",{"class":"c-location-hours-details"}).find("tbody").stripped_strings))
                        latitude = soup5.find("meta",{"itemprop":"latitude"})['content']
                        longitude = soup5.find("meta",{"itemprop":"longitude"})['content']
                        store3 =[]
                        store3.append(base_url)
                        store3.append(name)
                        store3.append(street_address)
                        store3.append(city)
                        store3.append(state)
                        store3.append(zip1)
                        store3.append("US")
                        store3.append(store_number)
                        store3.append(phone)
                        store3.append("<MISSING>")
                        store3.append(latitude)
                        store3.append(longitude)
                        store3.append(hours)
                        store3.append(page_url)
                        store3 = [str(x).strip() if x else "<MISSING>" for x in store3]
                        yield store3
                        # logger.info("========================================",store3)
    ## For WC location
    r_wc = session.get("https://www.autozone.com/locations/dc/washington.html", headers=headers)
    soup_wc = BeautifulSoup(r_wc.text, "lxml")
    for link in soup_wc.find_all("div",{"class":"c-location-grid-col col-lg-4 col-sm-5 col-xs-12"}):
        page_url = link.find("h5",class_="c-location-grid-item-title").find("a")["href"].replace("..","https://www.autozone.com/locations")
        # logger.info(page_url)
        # logger.info("page_url:444",page_url)
        name = link.find("h5",class_="c-location-grid-item-title").find("a").text.strip()
        try:
            store_number = (name.split("#")[1])
        except:
            store_number='<MISSING>'
        address = list(link.find("address",class_="c-address").stripped_strings)
        street_address = address[0].strip()
        city = address[1].strip()
        state = address[-3].strip()
        zip1 = address[-2].strip()
        country_code = "US"
        phone = link.find("span",{"itemprop":"telephone"}).text.strip()
        r6 = session.get(page_url,headers=headers)
        soup6 = BeautifulSoup(r6.text, "lxml")
        hours = " ".join(list(soup6.find("table",class_="c-location-hours-details").stripped_strings)).replace("Day of the Week Hours","").strip()
        latitude = soup6.find("meta",{"itemprop":"latitude"})['content']
        longitude = soup6.find("meta",{"itemprop":"longitude"})['content']
        store4 =[]
        store4.append(base_url)
        store4.append(name)
        store4.append(street_address)
        store4.append(city)
        store4.append(state)
        store4.append(zip1)
        store4.append("US")
        store4.append(store_number)
        store4.append(phone)
        store4.append("<MISSING>")
        store4.append(latitude)
        store4.append(longitude)
        store4.append(hours)
        store4.append(page_url)
        store4 = [str(x).strip() if x else "<MISSING>" for x in store4]
        yield store4
        # logger.info("========================================",store4)
def scrape():
    data = fetch_data()
    write_output(data)
scrape()


