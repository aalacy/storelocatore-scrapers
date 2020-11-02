import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



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
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://locations.umb.com/"
    r = session.get(base_url,headers = header)
    soup = BeautifulSoup(r.text,"lxml")
    href = soup.find('div',{'class':'region-map-list'}).find_all('div',{'class':'map-list-item'})
    location_urls = []
    for target_list in href:
        href  = target_list.find('a')['href']
        vr = session.get(href,headers = header)
        soup = BeautifulSoup(vr.text,"lxml")
        vk = soup.find('div',{'class':'col-maplist'}).find('div',{'class':'map-list-wrap'}).find('ul',{'class':'map-list'}).find_all('li',{'class':'map-list-item-wrap'})
        for target_list in vk:
            link = target_list.find('a',{'class':'ga-link'})['href']
            vr = session.get(link,headers = header)
            soup = BeautifulSoup(vr.text,"lxml")
            for location in soup.find("div",{"class":"map-list-tall"}).find_all("span",{"class":"location-name"}):
                location_url = location.parent["href"]
                if location_url in location_urls:
                    continue
                location_urls.append(location_url)
                location_request = session.get(location_url,headers=header)
                soup = BeautifulSoup(location_request.text,"lxml")
               
                geo_location = json.loads(soup.find('div',{'id':"gmap"}).find("script").text.split("defaultData = ")[1].split('};')[0] + "}")["markerData"][0]
                locator_domain = 'https://www.umb.com/'
                location_name  = location.text.strip()
                fb = soup.find('div',{'class':'address'}).find_all('div')
                street_address = ' '.join(list(fb[0].stripped_strings))
                temp = ' '.join(list(fb[1].stripped_strings)).split(',')
                city = temp[0]
                state = temp[1].strip().split(' ')[0]
                zip  = temp[1].strip().split(' ')[1]
                store_number = '<MISSING>'
                phone = soup.find('a',{'class':'phone'}).text
                country_code = 'US'
                location_type = '<MISSING>'
                latitude = geo_location["lat"]
                longitude = geo_location["lng"]
                if soup.find("div",{"class":"hours-col"}):
                    hours_soup = soup.find("div",{"class":"hours-col"})
                    [s.extract() for s in hours_soup('script')]
                    hours_of_operation = " ".join(list(hours_soup.stripped_strings))
                else:
                    hours_of_operation = "<MISSING>"
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
                store.append(location_url)
                yield store
        
def scrape():
    data = fetch_data()  
    
    write_output(data)

scrape()