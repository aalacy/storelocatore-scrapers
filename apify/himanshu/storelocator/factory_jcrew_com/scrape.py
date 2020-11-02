import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        for row in data:
            writer.writerow(row)


headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
base_url = "https://factory.jcrew.com/"

def scrape_data(url):
    location_soup =bs(session.get(url).content, "lxml")
    location_name = location_soup.find("h1",{"class":"Hero-title"}).text
    street_address = location_soup.find("meta",{"itemprop":"streetAddress"})['content']
    city = location_soup.find("meta",{"itemprop":"addressLocality"})['content']
    state = location_soup.find("abbr",{"itemprop":"addressRegion"}).text
    zipp= location_soup.find("span",{"itemprop":"postalCode"}).text
    country_code = location_soup.find("abbr",{"itemprop":"addressCountry"}).text
    phone  = location_soup.find("div",{"class":"Phone-display Phone-display--withLink"}).text.strip()
    latitude = location_soup.find("meta",{"itemprop":"latitude"})['content']
    longitude = location_soup.find("meta",{"itemprop":"longitude"})['content']
    try:
        hours_of_operation = " ".join(list(location_soup.find("table",{"class":"c-hours-details"}).stripped_strings)).replace("Day of the Week Hours","").strip()
    except:
        hours_of_operation = "<MISSING>"

    store = []
    store.append(base_url)
    store.append(location_name)
    store.append(street_address)
    store.append(city)
    store.append(state)
    store.append(zipp)
    store.append(country_code)
    store.append("<MISSING>")
    store.append(phone )
    store.append("<MISSING>")
    store.append(latitude)
    store.append(longitude)
    store.append(hours_of_operation)
    store.append(url)
    return store

def fetch_data():
    

    for country in ['https://stores.factory.jcrew.com/us','https://stores.factory.jcrew.com/ca']:


        soup = bs(session.get(country).content, "lxml")
    
        for state_link in soup.find_all("a",{"class":"Directory-listLink"}):

            if state_link['data-count'] == "(1)":

                page_url = "https://stores.factory.jcrew.com/" + state_link['href']
                data = scrape_data(page_url)
                yield data
                
            else:
            
                city_soup = bs(session.get("https://stores.factory.jcrew.com/"+state_link['href']).content, "lxml")

                if city_soup.find("a",{"class":"Directory-listLink"}):

                    for city_link in city_soup.find_all("a",{"class":"Directory-listLink"}):

                        if city_link['data-count'] == "(1)":

                            page_url = city_link['href'].replace("..","https://stores.factory.jcrew.com/")
                            data = scrape_data(page_url)
                            yield data

                        else:

                            link_soup = bs(session.get(city_link['href'].replace("..","https://stores.factory.jcrew.com/")).content, "lxml")

                            for url in link_soup.find_all("a",{"class":"Teaser-titleLink js-teaser-titlelink"}):
                        
                                page_url = url['href'].replace("../..","https://stores.factory.jcrew.com/")
                                data = scrape_data(page_url)
                                yield data
                else:
            
                    link_soup = bs(session.get("https://stores.factory.jcrew.com/"+state_link['href']).content, "lxml")

                    for url in link_soup.find_all("a",{"class":"Teaser-titleLink js-teaser-titlelink"}):
                        
                        page_url = url['href'].replace("../..","https://stores.factory.jcrew.com/")
                        data = scrape_data(page_url)
                        yield data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
