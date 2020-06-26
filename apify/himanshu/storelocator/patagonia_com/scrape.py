import csv
import requests
from bs4 import BeautifulSoup as bs
import re
import json
from datetime import datetime
from sgrequests import SgRequests

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    base_url = "https://www.patagonia.com"
    url_lst = ["https://www.patagonia.com/store-locator/?dwfrm_wheretogetit_country=US","https://www.patagonia.com/store-locator/?dwfrm_wheretogetit_country=CA"]
    for url in url_lst:
        soup = bs(session.get(url).content,"lxml")
        
        for store in soup.find_all("div",{"class":"store-name"}):
            location_name = store.a.text
            page_url = base_url + store.a['href']
            store_number = page_url.split("_")[1].split(".")[0]
            
            location_soup = bs(session.get(page_url).content, "lxml")
            try:
                addr = list(location_soup.find("div",{"class":"store-info-address"}).stripped_strings)
                street_address = addr[0]
                city = addr[1].split(",")[0]
                state = addr[1].split(",")[1].split()[0]
                zipp = " ".join(addr[1].split(",")[1].split()[1:])
                hours = "<MISSING>"
                lat = location_soup.find("div",{"class":"store-locator-map"})['data-latitude']
                lng = location_soup.find("div",{"class":"store-locator-map"})['data-longitude']
                if location_soup.find("div",{"class":"store-info-phone"}):
                    phone = location_soup.find("div",{"class":"store-info-phone"}).text.strip()
                else:
                    phone = "<MISSING>"

            except:
                
                street_address = location_soup.find_all("div",{"class":"Footer-business-info-item"})[1].text.replace(",","")
                addr = location_soup.find_all("div",{"class":"Footer-business-info-item"})[2].text.split(",")
                city = addr[0]
                state = addr[1].strip()
                zipp = addr[2].strip()
                phone = location_soup.find("a",{"class":"Footer-business-info-item Footer-business-info-item--phone"}).text
                hours = " ".join(list(location_soup.find("div",{"class":"Footer-business-hours"}).stripped_strings))

                json_data = json.loads(location_soup.find("script",{"data-name":"static-context"}).text.split("SQUARESPACE_CONTEXT =")[1].replace("]]}}};","]]}}}"))['website']['location']
                lat = json_data['mapLat']
                lng = json_data['mapLng']
           
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)   
            store.append("US" if zipp.replace("-","").isdigit() else "<MISSING>")
            store.append(store_number if store_number.isdigit() else "<MISSING>")
            store.append(phone)
            store.append("Patagonia Retail Stores")
            store.append(lat)
            store.append(lng)
            store.append(hours)
            store.append(page_url)     
         
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store

    ## Authorized Dealer location

    json_data = session.get("https://patagonia.locally.com/stores/conversion_data?has_data=true&company_id=30&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat=40.78831928091212&map_center_lng=-74.06000000000097&map_distance_diag=5000&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level=").json()['markers']

    for data in json_data:
        if data['country'] not in ["US","CA"]:
            continue
        location_name = data['name']
        street_address = data['address']
        city = data['city']
        state = data['state']
        zipp = data['zip']
        country_code = data['country']
        store_number = data['id']
        phone = data['phone']
        location_type = "Authorized Dealer"
        lat = data['lat']
        lng = data['lng']

        try:
            hours = ''
            if data['mon_time_open'] == 0 or data['mon_time_close'] == 0:
                hours+= "Mon Closed"
            else:
                hours+= "Mon"+" "+ datetime.strptime(str(data['mon_time_open']),"%H%M").strftime("%I:%M %p")+" - "+datetime.strptime(str(data['mon_time_close']),"%H%M").strftime("%I:%M %p")

            if data['tue_time_open'] == 0 or data['tue_time_close'] == 0:
                hours+= " Tue Closed"
            else:
                hours+= " Tue"+" "+ datetime.strptime(str(data['tue_time_open']),"%H%M").strftime("%I:%M %p")+" - "+datetime.strptime(str(data['tue_time_close']),"%H%M").strftime("%I:%M %p")

            if data['wed_time_open'] == 0 or data['wed_time_close'] == 0:
                hours+= " Wed Closed"
            else:
                hours+= " Wed"+" "+ datetime.strptime(str(data['wed_time_open']),"%H%M").strftime("%I:%M %p")+" - "+datetime.strptime(str(data['wed_time_close']),"%H%M").strftime("%I:%M %p")

            if data['thu_time_open'] == 0 or data['thu_time_close'] == 0:
                hours+= " Thu Closed"
            else:
                hours+= " Thu"+" "+ datetime.strptime(str(data['thu_time_open']),"%H%M").strftime("%I:%M %p")+" - "+datetime.strptime(str(data['thu_time_close']),"%H%M").strftime("%I:%M %p")

            if data['fri_time_open'] == 0 or data['fri_time_close'] == 0:
                hours+= " Fri Closed"
            else:
                hours+= " Fri"+" "+ datetime.strptime(str(data['fri_time_open']),"%H%M").strftime("%I:%M %p")+" - "+datetime.strptime(str(data['fri_time_close']),"%H%M").strftime("%I:%M %p")

            if data['sat_time_open'] == 0 or data['sat_time_close'] == 0:
                hours+= " Sat"+" "+"Closed"
            else:
                hours+= " Sat"+" "+ datetime.strptime(str(data['sat_time_open']),"%H%M").strftime("%I:%M %p")+" - "+datetime.strptime(str(data['sat_time_close']),"%H%M").strftime("%I:%M %p")

            if data['sun_time_open'] == 0 or data['sun_time_close'] == 0:
                hours+= "Sun Closed"
            else:
                hours+= " Sun"+" "+ datetime.strptime(str(data['sun_time_open']),"%H%M").strftime("%I:%M %p")+" - "+datetime.strptime(str(data['sun_time_close']),"%H%M").strftime("%I:%M %p")
        except:
            hours = "<MISSING>"

        store = []
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
        store.append("<MISSING>")     
        
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store

        


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
