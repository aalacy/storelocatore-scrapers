import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.ubs.com"
    try:
        r = session.get("https://www.ubs.com/locations/_jcr_content.lofisearch.all.en.data", headers=headers).json()
        
        for i in r['hits']['hits']:
            if "/en/ca" in str(i['fields']['id']) or "/en/us" in str(i['fields']['id']):

                if "/en/ca" in str(i['fields']['id']):
                    street_address = ''.join(str(i['fields']['bu_podAddress']).replace("['",'').replace("']",'').split(',')[:-1])
                    city = str(i['fields']['bu_podAddress']).replace("['",'').replace("']",'').split(',')[-1].split(' ')[1]
                    state = str(i['fields']['bu_podAddress']).replace("['",'').replace("']",'').split(',')[-1].split(' ')[2]
                    zipp = ' '.join(str(i['fields']['bu_podAddress']).replace("['",'').replace("']",'').split(',')[-1].split(' ')[3:])
                    latitude = str(i['fields']['latitude']).replace("[",'').replace("]",'')
                    longitude = str(i['fields']['longitude']).replace("[",'').replace("]",'')
                    location_type = str(i['fields']['pod_locationType']).replace("['",'').replace("']",'')
                    location_name = str(i['fields']['title']).replace("['",'').replace("']",'')
                    country_code = "CA"
                    link = "https://www.ubs.com/locations/_jcr_content.location._en_ca_"+str(city.replace(' ','-').lower())+"_"+str(street_address.replace(' ','-').lower())+".en.data"
                    r1 = session.get(link).json()
                    phone = r1['telephoneNumber']
                    href = "https://www.ubs.com"+str(r1['poDs'][0]['url'])

                    r4 = session.get(href)
                    soup1 = BeautifulSoup(r4.text, "lxml")  
                    hours = soup1.find("table",{"class":"loFi-poi__location__details__schedule__hours"})
                    if hours != None:  
                        hours_of_operation = ' '.join(list(hours.stripped_strings)[0:])
                    else:
                        hours_of_operation = "<MISSING>"
                    
                elif "/en/us" in str(i['fields']['id']):
                    street_address = ''.join(str(i['fields']['bu_podAddress']).replace("['",'').replace("']",'').replace('["','').split(',')[:-1])
                    city = str(i['fields']['bu_city']).replace("['",'').replace("']",'')
                    state = str(i['fields']['bu_podAddress']).split(',')[-1].split(' ')[-2]
                    zipp = str(i['fields']['bu_podAddress']).replace("']",'').replace('"]','').split(',')[-1].split(' ')[-1]
                    latitude = str(i['fields']['latitude']).replace("[",'').replace("]",'')
                    longitude = str(i['fields']['longitude']).replace("[",'').replace("]",'')
                    location_type = str(i['fields']['pod_locationType']).replace("['",'').replace("']",'')
                    location_name = str(i['fields']['title']).replace("['",'').replace("']",'')
                    country_code = "US"
                    link = "https://www.ubs.com/locations/_jcr_content.location._en_us_"+str(city.replace(' ','-').replace('.','').lower())+"_"+str(street_address.replace(' ','-').replace("'",'-').lower())+".en.data"
                    r2 = session.get(link).json()
                    for k in r2['poDs']:
                        href = "https://www.ubs.com"+str(k['url'])
                        
                        r3 = session.get(href)
                        soup = BeautifulSoup(r3.text, "lxml")  
                        if soup.find("dd",{"class":"loFi-details__detail__info__phone"}) != None:
                            phone = soup.find("dd",{"class":"loFi-details__detail__info__phone"}).text                    
                        else:
                            phone = "<MISSING>"
                        hours = soup.find("table",{"class":"loFi-poi__location__details__schedule__hours"})
                        if hours != None:  
                            hours_of_operation = ' '.join(list(hours.stripped_strings)[0:])
                        else:
                            hours_of_operation = "<MISSING>"
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
                store.append(location_type)
                store.append(latitude)
                store.append(longitude)
                store.append(hours_of_operation)
                store.append(href)
                yield store
    except:
        pass

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
