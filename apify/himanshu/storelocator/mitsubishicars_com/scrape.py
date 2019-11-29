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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url ="https://www.mitsubishicars.com"
    return_main_object=[]
    output=[]
    addressess =[]
    zps=sgzip.for_radius(50)
    for zp in zps:
        try:
            r=requests.get('https://www.mitsubishicars.com/rs/dealers?bust=1569242590201&zipCode='+zp+'&idealer=false&ecommerce=false').json()
        except:
            continue
        hours_of_operation = ''    
        for loc in r:
            if loc['zipcode']:
                # page_url = loc['dealerUrl']
                link = loc['dealerUrl'] 
                if link != None:
                    page_url = (link)
                    try:                        
                        r=requests.get("http://"+page_url.lower())
                    except:
                        continue
                    # r=requests.get("https://www.saltlakemitsubishi.com/")

                    
                    soup = BeautifulSoup(r.text, "lxml")
                    # , attrs = {'class' : 'pos'}
                    # columns = soup.findAll('tr', text = re.compile('HOURS'))
                    # .parent.find('table').find_all('tr')
                    # print("startttt")
                    main=soup.find('h3',text=re.compile("Hours"))
                    if main != None:
                        # print("================",main.parent)
                        if main.parent != None:
                            hours_of_operation = " ".join(list(main.parent.stripped_strings))
                        #     print(hours_of_operation)
                        # else:
                        #     print("http://"+page_url)

                        # main.parent.find(re.compile("tbody"))
                        # if main.parent.find(re.compile("tbody")) !=None:
                        #     hours_of_operation = " ".join(list(main.parent.find(re.compile("tbody")).stripped_strings))   
                        # else:              
                        #     
                # print()
                address=loc['address1'].strip()
                if loc['address2']:
                    address+=' '+loc['address2'].strip()
                name=loc['dealerName'].strip()
                city=loc['city'].strip()
                state=loc['state'].strip()
                zip=loc['zipcode']
                phone=loc['phone'].strip()
                country=loc['country'].strip()
                if country=="United States":
                    country="US"
                lat=loc['latitude']
                lng=loc['longitude']
                hour=''
                storeno=loc['bizId']
                store=[]
                store.append(base_url)
                store.append(name if name else "<MISSING>")
                store.append(address if address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zip if zip else "<MISSING>")
                store.append(country if country else "<MISSING>")
                store.append(storeno if storeno else "<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(lat if lat else "<MISSING>")
                store.append(lng if lng else "<MISSING>")
                store.append(hours_of_operation if hours_of_operation.strip() else "<MISSING>")
                store.append(page_url)
                # print(store)
                if store[2] in addressess:
                    continue
                addressess.append(store[2])
                yield store

                # store.append()
                # adrr =name+' '+address + ' ' + city + ' ' + state + ' ' + str(zip)
                # if adrr not in output:
                #     output.append(adrr)
                #     
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
