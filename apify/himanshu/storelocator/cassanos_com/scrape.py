import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url ="https://www.cassanos.com"
    
    r = session.get(base_url+'/online-ordering/')
    soup=BeautifulSoup(r.text,'lxml')
    
    for dt in soup.find('article',{"class":'all-locations'}).find_all("div",{"class":"location-block"}):
        page_url = dt.find("a")['href']
        
        
        location_soup = BeautifulSoup(session.get(page_url).text, "lxml")
        try:
            json_data = json.loads(location_soup.find(lambda tag: (tag.name == "script") and '"address"' in tag.text).text.split("var session =")[1].split("if(!window")[0].strip().replace("};","}"))
    
            location_name = json_data['store']['name']

            street_address = json_data['store']['address']

            if json_data['store']['address2']:
                street_address += " " + json_data['store']['address2']
            city = json_data['store']['city']
            state = json_data['store']['state']
            zipp = json_data['store']['zip']
            country_code = "US"
            store_number = json_data['store']['id']
            phone = json_data['store']['phone']
            location_type = "Restaurant"
            lat = json_data['store']['latitude']
            lng = json_data['store']['longitude']

            hours = "Monday " + json_data['store']['monday_display_hours'] \
                + " Tuesday " +json_data['store']['tuesday_display_hours'] \
                    + " Wednesday " +json_data['store']['wednesday_display_hours'] \
                        + " Thursday " +json_data['store']['thursday_display_hours'] \
                            + " Friday " +json_data['store']['friday_display_hours'] \
                                + " Saturday " +json_data['store']['saturday_display_hours'] \
                                    + " Sunday " +json_data['store']['sunday_display_hours'] 
        except:
            try:
                loc=list(location_soup.find('address',{'id':'rColAddress'}).stripped_strings)
                location_name=loc[0].strip()
                store_number=loc[0].split('#')[-1].strip()
                street_address=loc[1].strip()
                hours=' '.join(location_soup.find('div',{'id':'rColHours'}).stripped_strings).strip()
                phone=loc[-1].strip()
                ct=loc[2].split(',')
                city=ct[0].strip()
                state=ct[1].strip().split(' ')[0].strip()
                zipp=ct[1].strip().split(' ')[1].strip()
            except:
                loc=list(location_soup.find('span',{'id':'rColAddress'}).stripped_strings)
                location_name = loc[0]
                street_address = loc[1]
                store_number=loc[0].split('#')[-1].strip()
                city = loc[-1].split(",")[0]
                state = loc[-1].split(",")[1].split()[0]
                zipp = loc[-1].split(",")[1].split()[1]
                phone = location_soup.find("span",{"id":"rColPhone"}).text
                hours=' '.join(location_soup.find('span',{'id':'rColHours'}).stripped_strings).strip()
            lat = ''
            lng = ''
        
        store=[]
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(lat)
        store.append(lng)
        store.append(hours)
        store.append(page_url)
        store = [str(x).replace("–","-").encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
