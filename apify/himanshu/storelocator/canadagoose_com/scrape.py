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
    addresses = []
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.canadagoose.com/"

    page_url = "https://www.canadagoose.com/ca/en/find-a-retailer/find-a-retailer.html"

    r= session.get("https://hosted.where2getit.com/canadagoose/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E8949AAF8-550E-11DE-B2D5-479533A3DD35%3C%2Fappkey%3E%3Cformdata+id%3D%22getlist%22%3E%3Cobjectname%3EStoreLocator%3C%2Fobjectname%3E%3Climit%3E5000%3C%2Flimit%3E%3Corder%3Erank%3A%3Anumeric%3C%2Forder%3E%3Cwhere%3E%3Ccity%3E%3Cne%3EQuam%3C%2Fne%3E%3C%2Fcity%3E%3Ccountry%3E%3Ceq%3ECA%3C%2Feq%3E%3C%2Fcountry%3E%3C%2Fwhere%3E%3Cradiusuom%3E%3C%2Fradiusuom%3E%3C%2Fformdata%3E%3C%2Frequest%3E", headers=headers)

    soup = BeautifulSoup(r.text, "lxml")

    for i in soup.find_all("poi"):

        location_name = i.find("name").text

        if i.find("address1").text != '':
            street_address = i.find("address1").text + str(i.find("address2").text)
        else:
            street_address = "<MISSING>"

        city = i.find("city").text
        state = i.find("province").text

        if i.find("postalcode").text != '':
            zipp = i.find("postalcode").text
        else:
            zipp = "<MISSING>"

        country_code = "CA"

        if i.find("phone").text != '':
            phone = i.find("phone").text
        else:
            phone = "<MISSING>"

        latitude = i.find("latitude").text
        longitude = i.find("longitude").text

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append("<MISSING>") 
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append("<MISSING>")
        store.append(page_url)
        store = [x.strip() if x else "<MISSING>" for x in store]
        yield store

    r1 = session.get("https://hosted.where2getit.com/canadagoose/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E8949AAF8-550E-11DE-B2D5-479533A3DD35%3C%2Fappkey%3E%3Cformdata+id%3D%22getlist%22%3E%3Cobjectname%3EStoreLocator%3C%2Fobjectname%3E%3Climit%3E5000%3C%2Flimit%3E%3Corder%3Erank%3A%3Anumeric%3C%2Forder%3E%3Cwhere%3E%3Ccity%3E%3Cne%3EQuam%3C%2Fne%3E%3C%2Fcity%3E%3Ccountry%3E%3Ceq%3EUS%3C%2Feq%3E%3C%2Fcountry%3E%3C%2Fwhere%3E%3Cradiusuom%3E%3C%2Fradiusuom%3E%3C%2Fformdata%3E%3C%2Frequest%3E", headers=headers)

    soup1 = BeautifulSoup(r1.text, "lxml")

    for j in soup1.find_all("poi"):

        location_name = j.find("name").text

        if j.find("address1").text != '':
            street_address = j.find("address1").text + str(j.find("address2").text)
        else:
            street_address = "<MISSING>"

        city = j.find("city").text
        state = j.find("state").text

        if j.find("postalcode").text != '':
            zipp = j.find("postalcode").text
        else:
            zipp = "<MISSING>"

        country_code = "US"

        if j.find("phone").text != '':
            phone = j.find("phone").text
        else:
            phone = "<MISSING>"

        latitude = j.find("latitude").text
        longitude = j.find("longitude").text


        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp.replace('00000','<MISSING>'))
        store.append(country_code)
        store.append("<MISSING>") 
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append("<MISSING>")
        store.append(page_url)
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        store = [x.strip() if x else "<MISSING>" for x in store]
        yield store

def scrape():
    data = fetch_data()

    write_output(data)


scrape()
