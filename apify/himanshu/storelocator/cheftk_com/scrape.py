import csv
import requests
from bs4 import BeautifulSoup
import re
import json
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url ="http://www.cheftk.com"
    return_main_object=[]
    output=[]
    r=requests.get(base_url+"/contact-us.html")
    soup=BeautifulSoup(r.text,'lxml')
    bk = []

    for x in soup.find_all('a',{'class':'larger-map-link'}):
        bk.append(x.find_next('script').text.split(', { ')[1].split('},')[0].split(',')[1] +','+x.find_next('script').text.split(', { ')[1].split('},')[0].split(',')[2])


    main=soup.find_all('div',{'class':"wsb-element-text"})
    i = 0
    for dt in main:
        if dt.find('div',{"class":"txt"})!=None and dt.find('span',{'class':"editor_color_white"})!=None:
            arr=list(dt.stripped_strings)
            # arr = arr[arr == "\\u200b\\u200b"]
            detail=[]
            for mt in arr:
                if mt != '\u200b' and mt != '\u200b\u200b':
                    if mt:
                        detail.append(mt.replace("\xa0",' ').replace("\u200b",''))
            name=detail[0]
            if len(detail)>6:
                name+=' '+detail[1]
            hour=detail[-1].replace('  ','')
            phone=detail[-3].replace('Phone  : ','').strip()
            addr=detail[-4].split(',')
            storeno=''
            if len(addr) == 1:
                state=detail[-4].strip().split(' ')[0].strip()
                zip=detail[-4].strip().split(' ')[1].strip()
                addr1=detail[-5].split('#')
                address=addr1[0].strip()
                ct=addr1[1].strip().split(' ')
                storeno=ct[0]
                del ct[0]
                city=' '.join(ct).strip()
            else:
                address=addr[0].strip()
                city="<INACCESSIBLE>"
                state=addr[1].strip().split(' ')[0].strip()
                zip=addr[1].strip().split(' ')[1].strip()

            country = "US"
            lat = ''
            lng = ''

            if i == 2:
                lat=bk[0].strip().split(',')[0].replace('lat:','').strip()
                lng=bk[0].strip().split(',')[1].replace('lng:','').strip()
            if i == 3:

                lat = bk[1].strip().split(',')[0].replace('lat:', '').strip()
                lng = bk[1].strip().split(',')[1].replace('lng:', '').strip()

            page_url = base_url+"/contact-us.html"
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
            store.append(hour if hour.strip() else "<MISSING>")
            store.append(page_url if page_url.strip() else "<MISSING>")
            adrr =name+' '+address + ' ' + city + ' ' + state + ' ' + zip
            if adrr not in output:
                output.append(adrr)
                yield store
            i+=1

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
