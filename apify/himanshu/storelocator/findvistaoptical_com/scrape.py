import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://findvistaoptical.com"
    r = session.get("https://maps.findvistaoptical.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    app_key = soup.find("appkey").text

    location_request = session.get("https://maps.findvistaoptical.com/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E" + app_key + "%3C%2Fappkey%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Climit%3E250%3C%2Flimit%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3EAK%3C%2Faddressline%3E%3Clongitude%3E%3C%2Flongitude%3E%3Clatitude%3E%3C%2Flatitude%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Cwhere%3E%3Cand%3E%3Centityid%3E%3Ceq%3E17%3C%2Feq%3E%3C%2Fentityid%3E%3Cshowinlocatoryn%3E%3Ceq%3EY%3C%2Feq%3E%3C%2Fshowinlocatoryn%3E%3C%2Fand%3E%3C%2Fwhere%3E%3Csearchradius%3E50%7C100%7C5000%3C%2Fsearchradius%3E%3C%2Fformdata%3E%3C%2Frequest%3E")
    location_soup = BeautifulSoup(location_request.text,"lxml")

    for location in location_soup.find_all("poi"):
        name = location.find("name").text
        address = location.find("address1").text + location.find("address2").text
        city = location.find("city").text
        state = location.find("state").text
        zip_code = location.find("postalcode").text
        phone = location.find("phone").text
        country = location.find("country").text
        lat = location.find("latitude").text
        lng = location.find("longitude").text
        hours = location.find("schedule").text
        store = []
        store.append("http://findvistaoptical.com")
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip_code)
        store.append(country)
        store.append("<MISSING>")
        store.append(phone)
        store.append("vista optical")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
