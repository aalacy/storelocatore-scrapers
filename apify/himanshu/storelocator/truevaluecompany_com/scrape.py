import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
from sgrequests import SgRequests
session = SgRequests()



def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
   
    addresses = []

    base_url = "https://www.truevaluecompany.com"
    # time.sleep(1)
    # try:
        # r = request_wrapper('https://hosted.where2getit.com/truevalue/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E41C97F66-D0FF-11DD-8143-EF6F37ABAA09%3C%2Fappkey%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3E'+str(search.current_zip)+'%3C%2Faddressline%3E%3Clongitude%3E'+str(coord[1])+'%3C%2Flongitude%3E%3Clatitude%3E'+str(coord[0])+'%3C%2Flatitude%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Csearchradius%3E10%7C25%7C50%7C100%7C250%3C%2Fsearchradius%3E%3Cwhere%3E%3Cor%3E%3Ctv%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ftv%3E%3Chg%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fhg%3E%3Cgr%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fgr%3E%3Cds%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fds%3E%3Cja%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fja%3E%3Ctaylorrental%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ftaylorrental%3E%3C%2For%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E', "get", headers=headers)
    r = session.get("https://stores.truevalue.com/")
    soup = BeautifulSoup(r.text, "lxml")
    for state in soup.find_all("div",{"class":"itemlist"}):
        city_r = session.get(state.find("a")['href'])
        city_soup = BeautifulSoup(city_r.text, "lxml")
        for city in city_soup.find_all("div",{"class":"itemlist"}):
            location_r = session.get(city.find("a")['href'])
            location_soup = BeautifulSoup(location_r.text, "lxml")
            for url in location_soup.find_all("a",{"linktrack":"Landing page"}):
                page_url = url['href']
                store_r = session.get(page_url)
                store_soup = BeautifulSoup(store_r.text, "lxml")
                #print(page_url)
                raw_data = re.sub(r'\s+'," ",store_soup.find(lambda tag: (tag.name == "script") and "streetAddress" in tag.text).text.replace("//if applied, use the tmpl_var to retrieve the database value",'').replace("// starts services list",''))
                data = json.loads(raw_data.replace("}, ] ","} ]"))

                location_name = data['name'].replace('&#39;',"'")
                street_address = data['address']['streetAddress']
                city = data['address']['addressLocality']
                state = data['address']['addressRegion']
                zipp = data['address']['postalCode']
                country_code = data['address']['addressCountry']
                phone = data['telephone']
                store_number = data['@id']
                location_type = data['@type']
                latitude = data['geo']['latitude']
                longitude = data['geo']['longitude']
                hour = ''
                for time in  data['openingHoursSpecification']:
                    hour+= time['dayOfWeek'][0]+" "+ time['opens']+" "+time['closes']+" "
                hours = hour.strip()

        
                store = []
                store.append(base_url)
                store.append(location_name if location_name else "<MISSING>")
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append(country_code if country_code else "<MISSING>")
                store.append(store_number)
                store.append(phone if phone else "<MISSING>")
                store.append(location_type)
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hours if hours else "<MISSING>")
                store.append(page_url if page_url else "<MISSING>")
                if store[2] in addresses:
                    continue
                addresses.append(store[2])

                # print("data = " + str(store))
                # print(
                #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store
        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
#PR #L2S
