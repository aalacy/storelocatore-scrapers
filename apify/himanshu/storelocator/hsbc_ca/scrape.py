import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url ="https://www.hsbc.ca"
    cord=sgzip.coords_for_radius(100)
    return_main_object=[]
    output=[]
    addressess =[]
    # r=requests.get(base_url+"/1/2/contact-us/atm-branch-locations")
    # soup=BeautifulSoup(r.text,'lxml')
    # for zp in soup.find('map',{'id':'Map'}).find_all('area'):
    for cd in cord:
        #print(cd)
        # r1 = requests.get(base_url + zp['href'])
        # soup1 = BeautifulSoup(r.text, 'lxml')
        r2 = requests.get('https://www.hsbc.ca/1/PA_ABSL-JSR168/ABSLFCServlet?event=cmd_ajax&location_type=show-all-results&address=&cLat='+cd[0]+'&cLng='+cd[1]+'&LOCALE=en&rand=100').json()
        for dt in r2['results']:
            storeno=dt['location']['locationId']
            name = dt['location']['name']
            address=dt['location']['address']['postalAddress']
            address = dt['location']['address']['postalAddress']
            state = dt['location']['address']['province']
            city = dt['location']['address']['city']
            zip = dt['location']['address']['postalCode']
            country = dt['location']['address']['country']
            location_type = dt['location']['links']['details_tab']
            if country == "Canada":
                country="CA"
            # print("==========================================")
            # print(dt)
            lat=dt['location']['address']['lat']
            lng=dt['location']['address']['lng']
            store=[]
            phone=''
            hour=''
            if "services" in dt['location']:
                if dt['location']['services']:
                    hour=dt['location']['services'][0]
            if "WorkHrs" in dt['location']:
                for i in dt['location']['WorkHrs']['lobby']:
                   if  dt['location']['WorkHrs']['lobby'][i]=="-":
                        hour+=' '+i+' '+"Closed"
                   else:
                       hour+=' '+i+' '+dt['location']['WorkHrs']['lobby'][i]
            store.append(base_url)
            store.append(name if name else "<MISSING>")
            store.append(address if address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zip if zip else "<MISSING>")
            store.append(country if country else "<MISSING>")
            store.append(storeno if storeno else "<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append(location_type)
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hour if hour.strip() else "<MISSING>")
            store.append( "<MISSING>")
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            yield store
            # ads = address + ' ' + city + ' ' + state + ' ' + zip
            # if ads not in output:
            #     output.append(ads)
            #     return_main_object.append(store)
    # return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
