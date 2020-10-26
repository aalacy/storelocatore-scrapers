import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://octapharmaplasma.com/"

    return_main_object = []
    r = session.get(base_url)

    soup = BeautifulSoup(r.text,"lxml")
    States = soup.find("select", {"id": "States"})
    # get all <options> in a list
    options = States.find_all("option")


    # for each element in that list, pull out the "value" attribute
    values = [o.get("value") for o in options]
    values.pop(0)
    for idx, val in enumerate(values):
        getcenter = session.get(base_url + "/donor/donation-centers/"+val)
        getpage = BeautifulSoup(getcenter.text, "lxml")

        x = getpage.find('div',{'class':'articles--list'}).find_all('article',{'class':'clearfix'})

        for fb in x:
            geturl = fb.find('a')['href']
            getdata = session.get(base_url + geturl)
            getpagedata = BeautifulSoup(getdata.text, "lxml")

            getdt  = list(getpagedata.find('div',{'class':'s-grid6 m-grid8'}).stripped_strings)
            locator_domain = base_url
            location_name = getpagedata.find('header',{'class':'header--section'}).text.strip()
            street_address = getdt[1]
            city = getdt[2].split(',')[0]
            dd  = getdt[2].split(',')[1].strip().split(' ')
            state = dd[0]
            zip = ''
            if len(dd)>1:
                zip=dd[1]

            country_code = 'US'
            store_number = '<INACCESSIBLE>'
            location_type = ''

            latitude = ''
            longitude = ''
            if getpagedata.find('iframe') != None:
                if len(getpagedata.find('iframe')['src'].split('!2d')) == 2:
                    longitude =  getpagedata.find('iframe')['src'].split('!2d')[1].split('!3d')[0]
                   

                    latitude =  getpagedata.find('iframe')['src'].split('!2d')[1].split('!3d')[1].split('!2m')[0].split('!')[0]
                   

            
            phone =  getdt[4].replace('Phone','')
            page_url = base_url + "donor/donation-centers/"+val
            hours_of_operation =' '.join(list(getpagedata.find('ul',{'class':'list--hours'}).stripped_strings))
            if(phone != ""):
            
               

                store=[]
                store.append(locator_domain if locator_domain else '<MISSING>')
                store.append(location_name if location_name else '<MISSING>')
                store.append(street_address if street_address else '<MISSING>')
                store.append(city if city else '<MISSING>')
                store.append(state if state else '<MISSING>')
                store.append(zip if zip else '<MISSING>')
                store.append(country_code if country_code else '<MISSING>')
                store.append(store_number if store_number else '<MISSING>')
                store.append(phone if phone else '<MISSING>')
                store.append(location_type if location_type else '<MISSING>')
                store.append(latitude if latitude else '<MISSING>')
                store.append(longitude if longitude else '<MISSING>')
                store.append(hours_of_operation  if hours_of_operation else '<MISSING>')
                store.append(page_url  if page_url else '<MISSING>')
                # print("===",str(store))
                # return_main_object.append(store)
                yield  store

    # return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
