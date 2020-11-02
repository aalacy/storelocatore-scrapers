import csv
import requests
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    location_list = []
    base_url = "https://www.bigairusa.com"

    location_links = []
    location_name = None
    locator_domain = None
    street_address = None
    city = None
    state = None
    zip = None
    country_code = None
    store_number = "<MISSING>"
    phone = None
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = None

    for i, block in enumerate(BeautifulSoup(requests.get(base_url).content, 'html.parser').find_all(class_="fusion-text")):

        if i > 1:
            break

        li_tags = block.find_all("li")

        for li in li_tags:
            if li.a:
                link = li.a.get('href')
                soup = BeautifulSoup(requests.get(link).content, 'html.parser')
                address = soup.find(class_="contact-info-container").find(class_="address")
                
                if address:
                    address = address.get_text()
                    if address.find(" I ") > -1:
                        separator = " I "
                    else:
                        separator = " | "

                    street_address = address.split(separator)[0]
                    
                    if len(address.split(separator)) > 1:
                        city = address.split(separator)[1].split(", ")[0]
                        state = address.split(separator)[1].split(", ")[1]
                        zip = address.split(separator)[2]
                    else:
                        city = "<INACCESSIBLE>"
                        state = "<INACCESSIBLE>"
                        zip = "<INACCESSIBLE>"

                    country_code = "US"
                else:
                    continue
                    street_address = "<MISSING>"
                    city = "<MISSING>"
                    state = "<MISSING>"
                    zip = "<MISSING>"
                    country_code = "<MISSING>"
                location_name = city

                if soup.find(class_="phone") is None:
                    phone = "<MISSING>"
                else:
                    phone = soup.find(class_="phone").get_text()

                    if phone.find('•') > -1:
                        phone = phone.split('•')[0]
                
                locator_domain = link

                if soup.find(id="menu-item-1105"):
                    hours_link = soup.find(id="menu-item-1105").a.get("href")
                elif soup.find(id="menu-item-14"):
                    hours_link = soup.find(id="menu-item-14").a.get("href")
                elif soup.find(id="menu-item-21"):
                    hours_link = soup.find(id="menu-item-21").a.get("href")
                elif soup.find(id="menu-item-57"):
                    hours_link = soup.find(id="menu-item-57").a.get("href")
                elif soup.find(id="menu-item-1986"):
                    hours_link = soup.find(id="menu-item-1986").a.get("href")
                elif soup.find(id="menu-item-1902"):
                    hours_link = soup.find(id="menu-item-1902").a.get("href")
                elif soup.find(id="menu-item-1510"):
                    hours_link = soup.find(id="menu-item-1510").a.get("href")
                else:
                    hours_link = None

                
                if hours_link:
                    hours = BeautifulSoup(requests.get(hours_link).content, 'html.parser').find_all(class_="fusion-text")

                    for listing in hours: 
                        for i, child in enumerate(listing.find_all("li")):
                            if i ==0:
                                hours_of_operation = child.get_text() 
                            else:
                                hours_of_operation = hours_of_operation + ", " + child.get_text()
                    

                location_list.append([locator_domain, location_name, street_address, city, state, zip, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    return location_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
