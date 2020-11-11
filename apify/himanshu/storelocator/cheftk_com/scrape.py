import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
import html5lib
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',  encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    base_url ="http://www.cheftk.com/"
    
    output=[]
    soup = BeautifulSoup(session.get("http://www.cheftk.com/home.html", verify=False).text,'html5lib')
    a = soup.find_all('li',{'style':'width: auto'})
    for i in a:
        location_name=""
        street_address=""
        city=""
        state=""
        zipp =""
        country ="US"
        storeno =""
        phone=""
        lat=""
        lng=""
        hours_of_operation=""
        page_url=""
        if "chef-tk-catering-kona.html" in  i.find('a')['href'] :
            r1=session.get(base_url+"/chef-tk-catering-kona.html")
            soup1=BeautifulSoup(r1.text,'html5lib')
            b = soup1.find_all('div',{'class':'editor_color_green'})
            location_name = b[0].text
            street_address = " ".join(b[1].text.split(" ")[0:6])
            city = " ".join(b[1].text.strip().split(" ")[6:8])
            state = (b[1].text.strip().split(" ")[8])
            zipp = (b[1].text.strip().split(" ")[9])
            phone = (b[2].text.strip().split(":")[1])
            hours_of_operation = (b[3].text.strip().split(":")[1])
            page_url = base_url+"/chef-tk-catering-kona.html"
        if "snow-factory-tk-kona.html" in  i.find('a')['href']:
            r2 = session.get(base_url+"/snow-factory-tk-kona.html")
            soup2=BeautifulSoup(r2.text,'html5lib')
            c = soup2.find_all('div',{'id':'wsb-element-a976612f-12fc-4516-b514-9f303f2c12d3'})
            street_address = " ".join(c[0].text.strip().split(" ")[0:3])
            city = (c[0].text.split( )[3])
            state = (c[0].text.split( )[4])
            zipp = (c[0].text.split( )[5].replace("96740(808)","96740"))
            phone = (c[0].text.split( )[6].replace("327-0070","(808)327-0070"))
            page_url = base_url+"/snow-factory-tk-kona.html"
        if "gal-bi-808-bbq-mixed-plate.html" in  i.find('a')['href'] :
            r3=session.get(base_url+"/gal-bi-808-bbq-mixed-plate.html")
            soup3=BeautifulSoup(r3.text,'html5lib')
            d = soup3.find_all('div',{'id':'wsb-element-57392ce1-dbea-4e87-93bf-eea49952ba45'})
            for h in d:
                zipp = (h.text.split()[-2].split("(")[0])
                phone = (h.text.split()[-2].split("(")[1].replace("808)","(808)"))+ (h.text.split()[-1])
                state = (h.text.split()[-3])
                city = (h.text.split()[-4])
                street_address = " ".join(h.text.split()[5:8]).split("te")[1]
                location_name =" ".join(h.text.split()[0:6]).split("79")[0]
                page_url = base_url+"/gal-bi-808-bbq-mixed-plate.html"
        if "tk-noodle-house-kainaliu.html" in  i.find('a')['href'] :
            r3=session.get(base_url+"/tk-noodle-house-kainaliu.html")
            soup3=BeautifulSoup(r3.text,'html5lib')
            d = soup3.find_all('span',{'style':'font-family:jacques francois shadow;'})
            location_name =(d[0].text)
            street_address = (d[1].text)+" "+(d[2].text)
            city = (d[3].text).split( )[0]
            state = (d[3].text).split( )[1]
            zipp = (d[3].text).split( )[2]
            phone = (d[4].text)
            page_url = base_url+"/tk-noodle-house-kainaliu.html"
        store=[]
        store.append(base_url)
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country if country else "<MISSING>")
        store.append(storeno if storeno else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")
        if "<MISSING>" in store[3]:
            pass
        else:
             yield store

    base_url ="http://www.cheftk.com/"
    
    output=[]
    r=session.get(base_url+"/contact-us.html")
    soup=BeautifulSoup(r.text,'html5lib')
    bk = []

    for x in soup.find_all('a',{'class':'larger-map-link'}):
        bk.append(x.find_next('script').text.split(', { ')[1].split('},')[0].split(',')[1] +','+x.find_next('script').text.split(', { ')[1].split('},')[0].split(',')[2])


    main=soup.find_all('div',{'class':"wsb-element-text"})
    i = 0
    for dt in main:
        if dt.find('div',{"class":"txt"})!=None and dt.find('span',{'class':"editor_color_white"})!=None:
            arr=list(dt.stripped_strings)
            
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
                for i in range(len(store)):
                    if type(store[i]) == str:
                        store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
                store = [x.replace("–","-") if type(x) == str else x for x in store]
                store = [x.strip() if type(x) == str else x for x in store]
                yield store
            i+=1
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
