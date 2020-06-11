import csv
import os
import requests
from bs4 import BeautifulSoup
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].strip().split(' ')
    state = prov_zip[0].strip()
    zip_code = prov_zip[1].strip()

    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.pizzicatopizza.com/locations'
    ext = 'locations'
    r = requests.get(locator_domain)
    soup = BeautifulSoup(r.text,"lxml")
    # for q in soup.find("section",{"id":"stores"}).find("div",{"class":"row sqs-row"}).find("div",class_="col sqs-col-8 span-8").find_all("div",class_="col sqs-col-3 span-3"):
    #     p = q.find_all("p")
    #     for index,w in enumerate(q.find_all("h2")):
    #         location_name = w.text
    #         phone_number = list(p[index].stripped_strings)[0]
    #         street_address = list(p[index].stripped_strings)[1]
    #         city = list(p[index].stripped_strings)[2].split(',')[0]
    #         state = list(p[index].stripped_strings)[2].split(',')[1].strip().split( )[0]
    #         zip_code = list(p[index].stripped_strings)[2].split(',')[1].strip().split( )[1]
    #         hours_of_operation = " ".join(list(p[index].stripped_strings)[3:])
    #         country_code = 'US'
    #         store_number = '<MISSING>'
    #         location_type = '<MISSING>'
    #         lat = '<MISSING>'
    #         longit = '<MISSING>'
    #         hours = '<MISSING>'

    #         store_data = ["https://www.pizzicatopizza.com/", location_name, street_address, city, state, zip_code, country_code,
    #                       store_number, phone_number, location_type, lat, longit, hours]
    #         yield store_data

    for q in soup.find("section",{"id":"stores"}).find("div",{"class":"row sqs-row"}).find_all("div",class_="col sqs-col-3 span-3"):
        p = q.find_all("p")
        for index,w in enumerate(q.find_all("h2")):
            location_name = w.text
            # print(location_name)
            phone_number = list(p[index].stripped_strings)[0]
            street_address = list(p[index].stripped_strings)[1]
            city = list(p[index].stripped_strings)[2].split(',')[0]
            state = list(p[index].stripped_strings)[2].replace("Portland OR 97202",'Portland, OR 97202').split(',')[1].strip().split( )[0]
            zip_code = list(p[index].stripped_strings)[2].replace("Portland OR 97202",'Portland, OR 97202').split(',')[1].strip().split( )[1]
            hours_of_operation = " ".join(list(p[index].stripped_strings)[3:])
            country_code = 'US'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            lat = '<MISSING>'
            longit = '<MISSING>'
            hours = '<MISSING>'
            page_url = '<MISSING>'
            store_data = ["https://www.pizzicatopizza.com/", location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours_of_operation,page_url]
            yield store_data





def scrape():
    data = fetch_data()
    write_output(data)

scrape()
