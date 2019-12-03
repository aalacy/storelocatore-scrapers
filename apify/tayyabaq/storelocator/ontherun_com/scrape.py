from bs4 import BeautifulSoup
import csv
import requests
import json

url = "http://ontherun.com/site/store-locator"
json_url = 'http://www.ontherun.com//site/locator/json/0/0/0'
html = requests.get(json_url).json()
print(len(html))

def write_output(data):
    with open('OnTR.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    datas_list = []

    for item in html:
        try:
            zp = item['zip']
        except Exception as e:
            zp = "<MISSING>"

        try:
            st = item['state']
        except Exception as e:
            st = "<MISSING>"

        try:
            adrs = item['address']
        except Exception as e:
            adrs = "<MISSING>"

        try:
            ct = item['city']
        except Exception as e:
            ct = "<MISSING>"

        try:
            lat = item['latitude']
        except Exception as e:
            lat = "<MISSING>"

        try:
            long = item['longitude']
        except Exception as e:
            long = "<MISSING>"

        try:
            ph = item['phone']
            if len(ph) < 3:
                ph = "<MISSING>"
        except Exception as e:
            ph = "<MISSING>"

        try:
            link = item['url']
            if len(link) < 3:
                link = "<MISSING>"
        except Exception as e:
            link = "<MISSING>"

        try:
            hoo = item['open24']
            if item['open24'] == "0":
                hoo = "<MISSING>"
            else:
                hoo = "Open 24hrs"

        except Exception as e:
            hoo = "<MISSING>"

        try:
            ltype = item['gasbrand']
            if len(item['gasbrand']) < 1:
                ltype = "<MISSING>"

        except Exception as e:
            ltype = "<MISSING>"

        location_name = "On the Run"
        country_code = "US"
        store_numbr = "<MISSING>"
        locator_domain = "http://ontherun.com/site/"

        new_list = [locator_domain, link, location_name, adrs, ct, st, zp, country_code,
                    store_numbr, ph, ltype, lat, long, hoo]

        datas_list.append(new_list)
    return datas_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
