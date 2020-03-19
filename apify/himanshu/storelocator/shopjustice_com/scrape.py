import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
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
    base_url = "https://www.shopjustice.com/"

    r_state = session.get("https://stores.shopjustice.com/directory")
    soup_state = BeautifulSoup(r_state.text, "lxml")

    for state_link in soup_state.find_all("a",{"class":"Directory-listLink"}):
        s_link = state_link['href']
        if state_link['data-count'] == "(1)":
            page_url = "https://stores.shopjustice.com/"+s_link
            location_r = session.get(page_url)
            location_soup = BeautifulSoup(location_r.text, "lxml")

            location_name = " ".join(list(location_soup.find("h1",{"class":"Hero-title"}).stripped_strings))
            
            if location_soup.find("span",{"class":"c-address-street-2"}):
                street_address = location_soup.find("span",{"class":"c-address-street-1"}).text.strip() +" "+ location_soup.find("span",{"class":"c-address-street-2"}).text.strip()
            else:
                street_address = location_soup.find("span",{"class":"c-address-street-1"}).text.strip()
            city = location_soup.find("span",{"class":"c-address-city"}).text.strip()
            state = location_soup.find("abbr",{"class":"c-address-state"}).text.strip()
            zipp = location_soup.find("span",{"class":"c-address-postal-code"}).text.strip()
            phone = location_soup.find("div",{"itemprop":"telephone"}).text
            latitude = location_soup.find("meta", {"itemprop":"latitude"})['content']
            longitude = location_soup.find("meta", {"itemprop":"longitude"})['content']
            store_number = location_soup.find_all("span",{"class":"c-bread-crumbs-name"})[-1].text.replace("#","").strip()
            hours = " ".join(list(location_soup.find("table",{'class':"c-hours-details"}).stripped_strings)).replace("Day of the Week Hours","").strip()
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp )
            store.append("US" if zipp.replace("-","").isdigit() else "CA")
            store.append(store_number)
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append(page_url)
            # print("data ==="+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~````")
            yield store
        else:
            city_link = "https://stores.shopjustice.com/"+state_link['href']
            city_r = session.get(city_link)
            city_soup = BeautifulSoup(city_r.text, "lxml")

            for location in city_soup.find_all("a",{"class":"Directory-listLink"}):
                if location['data-count'] == "(1)":
                    page_url = "https://stores.shopjustice.com/"+location['href']
                    location_r = session.get(page_url)
                    location_soup = BeautifulSoup(location_r.text, "lxml")
                    location_name = " ".join(list(location_soup.find("h1",{"class":"Hero-title"}).stripped_strings))
            
                    if location_soup.find("span",{"class":"c-address-street-2"}):
                        street_address = location_soup.find("span",{"class":"c-address-street-1"}).text.strip() +" "+ location_soup.find("span",{"class":"c-address-street-2"}).text.strip()
                    else:
                        street_address = location_soup.find("span",{"class":"c-address-street-1"}).text.strip()
                    city = location_soup.find("span",{"class":"c-address-city"}).text.strip()
                    state = location_soup.find("abbr",{"class":"c-address-state"}).text.strip()
                    zipp = location_soup.find("span",{"class":"c-address-postal-code"}).text.strip()
                    phone = location_soup.find("div",{"itemprop":"telephone"}).text
                    latitude = location_soup.find("meta", {"itemprop":"latitude"})['content']
                    longitude = location_soup.find("meta", {"itemprop":"longitude"})['content']
                    store_number = location_soup.find_all("span",{"class":"c-bread-crumbs-name"})[-1].text.replace("#","").strip()
                    hours = " ".join(list(location_soup.find("table",{'class':"c-hours-details"}).stripped_strings)).replace("Day of the Week Hours","").strip()


                    store = []
                    store.append(base_url)
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp )
                    store.append("US" if zipp.replace("-","").isdigit() else "CA")
                    store.append(store_number)
                    store.append(phone)
                    store.append("<MISSING>")
                    store.append(latitude)
                    store.append(longitude)
                    store.append(hours)
                    store.append(page_url)
                    # print("data ==="+str(store))
                    # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~````")
                    yield store
                else:
                    store_link = "https://stores.shopjustice.com/"+location['href']
                    store_r = session.get(store_link)
                    store_soup = BeautifulSoup(store_r.text, "lxml")

                    for location in store_soup.find_all("a",{"class":"Teaser-titleLink"}):
                        page_url = location['href'].replace("..","https://stores.shopjustice.com")
                        location_r = session.get(page_url)
                        location_soup = BeautifulSoup(location_r.text, "lxml")
                        location_name = " ".join(list(location_soup.find("h1",{"class":"Hero-title"}).stripped_strings))
                
                        if location_soup.find("span",{"class":"c-address-street-2"}):
                            street_address = location_soup.find("span",{"class":"c-address-street-1"}).text.strip() +" "+ location_soup.find("span",{"class":"c-address-street-2"}).text.strip()
                        else:
                            street_address = location_soup.find("span",{"class":"c-address-street-1"}).text.strip()
                        city = location_soup.find("span",{"class":"c-address-city"}).text.strip()
                        state = location_soup.find("abbr",{"class":"c-address-state"}).text.strip()
                        zipp = location_soup.find("span",{"class":"c-address-postal-code"}).text.strip()
                        phone = location_soup.find("div",{"itemprop":"telephone"}).text
                        latitude = location_soup.find("meta", {"itemprop":"latitude"})['content']
                        longitude = location_soup.find("meta", {"itemprop":"longitude"})['content']
                        store_number = location_soup.find_all("span",{"class":"c-bread-crumbs-name"})[-1].text.replace("#","").strip()
                        hours = " ".join(list(location_soup.find("table",{'class':"c-hours-details"}).stripped_strings)).replace("Day of the Week Hours","").strip()


                        store = []
                        store.append(base_url)
                        store.append(location_name)
                        store.append(street_address)
                        store.append(city)
                        store.append(state)
                        store.append(zipp )
                        store.append("US" if zipp.replace("-","").isdigit() else "CA")
                        store.append(store_number)
                        store.append(phone)
                        store.append("<MISSING>")
                        store.append(latitude)
                        store.append(longitude)
                        store.append(hours)
                        store.append(page_url)
                        # print("data ==="+str(store))
                        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~````")
                        yield store



   
    

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
