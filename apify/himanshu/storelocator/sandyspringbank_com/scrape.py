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

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url ="https://www.sandyspringbank.com"
    return_main_object=[]
    output=[]
    headers={"Content-type": "application/x-www-form-urlencoded","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"}
    cord=sgzip.coords_for_radius(50)
    for cr in cord:
        try:
            data="lat="+cr[0]+"&lng="+cr[1]+"&searchby=FCS%7C&SearchKey=&rnd=1568716953234"
            r = session.post("https://sandyspringbankv2.locatorsearch.com/GetItems.aspx",headers=headers,data=data)
            r1=re.sub(r'\<\!\[CDATA\[',' ',r.text)
            r1=re.sub(r'\]\]\>',' ',r1)
            soup=BeautifulSoup(r1,'lxml')
            for loc in soup.find_all('marker'):
                lat=loc['lat']
                lng=loc['lng']
                name=loc.find('title').text.strip()
                address=loc.find('add1').text.strip()
                ctt=list(loc.find('add2').stripped_strings)
                ct=ctt[0].split(',')
                city=ct[0].strip()
                state=ct[1].strip().split(' ')[0].strip()
                zip=ct[1].strip().split(' ')[1].strip()
                phone=""
                if len(ctt)>1:
                    phone=ctt[-1].strip()
                country="US"
                storeno=''
                hour = ''
                hr=list(loc.find('label',text=re.compile('Hours')).parent.find('contents').stripped_strings)
                del hr[0]
                for h in hr:
                    if h=="Details":
                        break
                    hour+=" "+h
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
                store.append("sandyspringbank")
                store.append(lat if lat else "<MISSING>")
                store.append(lng if lng else "<MISSING>")
                store.append(hour.strip() if hour.strip() else "<MISSING>")
                adrr =name+' '+address + ' ' + city + ' ' + state + ' ' + zip
                if adrr not in output:
                    output.append(adrr)
                    return_main_object.append(store)
        except:
            continue
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
