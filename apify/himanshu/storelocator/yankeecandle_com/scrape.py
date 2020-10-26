import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        
    }
    addresses = []
    base_url = "https://www.yankeecandle.com"
    #usa location
    url= "https://www.yankeecandle.com/stores"
    try:
        r = session.get(url, headers=headers)
    except:
        pass
    soup= BeautifulSoup(r.text,"lxml")
    link = soup.find("div",{"class":"stateList"})
    for i in link.find_all("a"):
        m = (base_url +i['href'])
        r1 = session.get(m)
        soup1= BeautifulSoup(r1.text,"lxml")
        data =  (soup1.find(lambda tag: (tag.name ==  "script" and "__NEXT_DATA__" in tag.text)).text.split("__NEXT_DATA__ =")[1].split("module={}")[0])
        json_data = json.loads(data)
        for h in json_data['props']['pageData']['storesData']:
            k = (h['stores'])
            
            for j in k:
                dictionary = {'1':"Authorized Retailer",'2':"Yankee Candle",'3':"Outlet",'5':"Woodwick"}
                location_type = dictionary[str(h['type'])]
                

                location_name = (j['label'])
                street_address = (j['address']+" "+j['address2'])
                city = (j['city'])
                zipp = (j['zip'])
                phone = (j['phone'])

                
                store_number = (j['id'])
                state = j['state']['abbr']
                if "https://www.google.com" not in j['ctaUrl']:
                    page_url = base_url +j['ctaUrl']
                else:
                    page_url = m
                
                r2 = session.get(page_url, headers=headers)
                soup2 = BeautifulSoup(r2.text, "lxml")
                if soup2.find(lambda tag: (tag.name ==  "script" and "latitude" in tag.text)):
                    latitude =  (soup2.find(lambda tag: (tag.name ==  "script" and "latitude" in tag.text)).text.split('{"latitude":"')[1].split('","longitude":"')[0])
                    longitude = (soup2.find(lambda tag: (tag.name ==  "script" and "latitude" in tag.text)).text.split('{"latitude":"')[1].split('","longitude":"')[1].split('","zoomLevel"')[0])
                else:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                
                regHours1 = ''
                specialHours1 = ''
                if 'regHours' in j : 
                    for p in  j['regHours']:
                        regHours1 =regHours1+' '+(p['day']+" "+p['open']+"am-"+p['close']+"pm").replace('21:00pm','9:00pm').replace('18:00pm','6:00pm').replace('13:00am','1:00pm').replace('00:00am-06:00pm','12:00am-6:00pm').replace("20:00","8:00").replace("22:00","10:00").replace("21:30","09:30").replace("17:00","5:00").replace("19:00","7:00").replace("12:00am","12:00pm").replace("00:00am-5:00pm","12:00am-5:00pm").replace("23:00","11:00").replace("20:30","8:30").replace("17:30","5:30")
                if 'specialHours' in j :
                    for o in  j['specialHours']:
                        specialHours1 =specialHours1+' '+(o['dayDisplay']+" "+o['day']+" "+o['open']+"am-"+o['close']+"pm").replace("18:00","6:00").replace("21:00","9:00").replace("17:00","5:00").replace("24:00","12:00")
                hours_of_operation = (regHours1+' '+specialHours1).strip()
                store = []
                store.append("https://www.yankeecandle.com")
                store.append(location_name.replace('&amp;','') if location_name else "<MISSING>") 
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp)
                store.append("US")
                store.append(store_number if store_number else "<MISSING>") 
                store.append(phone if phone else "<MISSING>")
                store.append(location_type)
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hours_of_operation if hours_of_operation else "<MISSING>")
                store.append(page_url)
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
                yield store
    # canada location
    canada_r = session.get("https://www.yankeecandle.com/stores/ontario", headers=headers)
    canada_soup = BeautifulSoup(canada_r.text, "lxml")
    data_canada =  (canada_soup.find(lambda tag: (tag.name ==  "script" and "__NEXT_DATA__" in tag.text)).text.split("__NEXT_DATA__ =")[1].split("module={}")[0])
    json_data1 = json.loads(data_canada)
    for h1 in json_data1['props']['pageData']['storesData']:
        k1 = (h1['stores'])
        for j1 in k1:
            dictionary = {'1':"Authorized Retailer",'2':"Yankee Candle",'3':"Outlet",'5':"Woodwick"}
            location_type = dictionary[str(h1['type'])]
            # print(location_type)
            location_name = (j1['label'])
            street_address = (j1['address']+" "+j1['address2'])
            city = (j1['city'])
            zipp = (j1['zip'])
            phone = (j1['phone'])
            page_url = base_url +(j1['ctaUrl'])
            store_number = (j1['id'])
            state = j1['state']['abbr']
            regHours11 = ''
            specialHours1 = ''
            if 'regHours' in j1 : 
                for p1 in  j1['regHours']:
                    regHours11 =regHours11+' '+(p1['day']+" "+p1['open']+"am-"+p1['close']+"pm").replace('21:00pm','9:00pm').replace('18:00pm','6:00pm').replace('13:00am','1:00pm').replace('00:00am-06:00pm','12:00am-6:00pm').replace("20:00","8:00").replace("22:00","10:00").replace("21:30","09:30").replace("17:00","5:00").replace("19:00","7:00").replace("12:00am","12:00pm").replace("00:00am-5:00pm","12:00am-5:00pm").replace("23:00","11:00").replace("20:30","8:30").replace("17:30","5.30")
            if 'specialHours' in j1 :
                for o1 in  j1['specialHours']:
                    specialHours1 =specialHours1+' '+(o1['dayDisplay']+" "+o1['day']+" "+o1['open']+"am-"+o1['close']+"pm").replace("18:00","6:00").replace("21:00","9:00").replace("17:00","5:00").replace("24:00","12:00")
            hours_of_operation = (regHours11+' '+specialHours1).strip()
            r3 = session.get(page_url, headers=headers)
            soup3 = BeautifulSoup(r3.text, "lxml")              
            latitude =  (soup3.find(lambda tag: (tag.name ==  "script" and "latitude" in tag.text)).text.split('{"latitude":"')[1].split('","longitude":"')[0])
            longitude = (soup3.find(lambda tag: (tag.name ==  "script" and "latitude" in tag.text)).text.split('{"latitude":"')[1].split('","longitude":"')[1].split('","zoomLevel"')[0])
            store = []
            store.append("https://www.yankeecandle.com")
            store.append(location_name.replace('&amp;','') if location_name else "<MISSING>") 
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp.replace('910071900','91007-1900'))
            store.append("CA")
            store.append(store_number if store_number else "<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append(location_type)
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(page_url)
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
