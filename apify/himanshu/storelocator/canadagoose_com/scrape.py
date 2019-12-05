
import csv
import requests
from bs4 import BeautifulSoup
import re
import json



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    arr=["US","CA"]
    return_main_object = []
    return_main_object1 = []
    addressess =[]
    for i in range(len(arr)):
        base_url1 ='https://hosted.where2getit.com/canadagoose/ajax?xml_request=<request><appkey>8949AAF8-550E-11DE-B2D5-479533A3DD35</appkey><formdata id="getlist"><objectname>StoreLocator</objectname><limit>5000</limit><order>rank::numeric</order><where><city><ne>Quam</ne></city><country><eq>'+str(arr[i])+'</eq></country></where><radiusuom></radiusuom></formdata></request>'
        r1 = requests.get(base_url1)
        main_soup1 = BeautifulSoup(r1.text, "lxml")

        name =  main_soup1.find_all("name")
        st = main_soup1.find_all("address1")
        city = main_soup1.find_all("city")
        lat = main_soup1.find_all("latitude")
        lon = main_soup1.find_all("longitude")
        phone  = main_soup1.find_all("phone")
        state = main_soup1.find_all("state")
        postalcode= main_soup1.find_all("postalcode")
        state = main_soup1.find_all("state")
        country =  main_soup1.find_all("country")
        
        for i in range(len(st)):
            tem_var=[]
            # print(country[i])
            tem_var.append("https://www.canadagoose.com")
            tem_var.append(name[i].text.encode('ascii', 'ignore').decode('ascii'))
            tem_var.append(st[i].text.encode('ascii', 'ignore').decode('ascii') if st[i].text.encode('ascii', 'ignore').decode('ascii') else "<MISSING>")
            tem_var.append(city[i].text.encode('ascii', 'ignore').decode('ascii'))
            tem_var.append(state[i].text.encode('ascii', 'ignore').decode('ascii'))
            if postalcode[i].text.encode('ascii', 'ignore').decode('ascii')=="0":
                tem_var.append("<MISSING>")
            else:
                tem_var.append(postalcode[i].text.encode('ascii', 'ignore').decode('ascii').replace("00000","<MISSING>"))

            tem_var.append(country[i].text.encode('ascii', 'ignore').decode('ascii'))
            tem_var.append("<MISSING>")
            tem_var.append(phone[i].text.encode('ascii', 'ignore').decode('ascii') if phone[i].text.encode('ascii', 'ignore').decode('ascii') else "<MISSING>") 
            tem_var.append("<MISSING>")
            tem_var.append(lat[i].text.encode('ascii', 'ignore').decode('ascii'))
            tem_var.append(lon[i].text.encode('ascii', 'ignore').decode('ascii'))
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            # print(tem_var)
            if tem_var[2] in addressess and tem_var[-4]:
                continue
            addressess.append(tem_var[2])
            if "SoHo 101 Wooster Street" in tem_var or "800 Boylston St" in tem_var or "6455 Macleod Trail SW" in tem_var or "1200 Morris Turnpike" in tem_var or "1020 Saint-Catherine St W" in tem_var:
                pass
            else:
                yield tem_var

    base_url = "https://www.canadagoose.com/ca/en/find-a-retailer/find-a-retailer.html"
    r = requests.get(base_url)
    main_soup = BeautifulSoup(r.text, "lxml")
    k = main_soup.find("div", {'class': "store-holder"})
    store_names = []
    street_address1 = []
    city1 = []
    state1 = []
    zip1 = []
    country_code = []
    phone1 = []
    latitude = []
    longitude = []
    return_main_object = []
    hours_of_operation = []
    names = k.find_all('h3', {'class': 'section-break'})
    for i in names:
        name = (i.span.find_next_siblings('span'))
        for j in name:
            store_names.append(j.text)
    adds = k.find_all('span', {'itemprop': "streetAddress"})
    locality = k.find_all('span', {'itemprop': "addressLocality"})
    state = k.find_all('span', {'itemprop': "addressRegion"})
    code = k.find_all('span', {'itemprop': "postalCode"})
    phone = k.find_all('span', {'itemprop': "telephone"})
    for add in adds:
        street_address1.append(add.text.replace('\n', '').replace('  ', '').replace('\r', ''))

    for i in locality:
        city1.append(i.text)

    for i in state:
        state1.append(i.text)

    for i in code:
        if i.text:
            zip1.append(i.text)
        else:
            zip1.append("<MISSING>")
    
    for i in zip1:
        if "<MISSING>" in i:
             country_code.append("<MISSING>")
        else:
            if len(i)==5:
                country_code.append("US")
            else:
                country_code.append("CA")

    for i in phone:
        phone1.append(i.text)
    link = k.find_all('a', {'class': "more-info", 'title': "More info"})
    for i in link:
        time = ''
        url = i['href']
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        k1 = soup.find("div", {"class": "store-info desktop"})
        times = k1.find_all('meta')
        list1 = []
        a = k1.find_all('a', {'class': "button"})
        for i in a:
            if len(i['href'].split('/@')[-1].split(",")) != 1:
                latitude.append(i['href'].split('/@')[-1].split(",")[0])
                longitude.append(i['href'].split('/@')[-1].split(",")[1]) 
            else:
                latitude.append("<MISSING>")
                longitude.append("<MISSING>")
  
        if times:
            for i in times:
                time = time + ' ' + (i.get('content'))
        else:
            time = time + ' ' + ("<MISSING>")
        hours_of_operation.append(time.strip())

    for i in range(len(store_names)):
        store = []
        store.append("https://www.canadagoose.com")
        store.append(store_names[i].replace("\uff0b",""))
        store.append(street_address1[i].replace("\uff0b","").replace("Mall of America ","").replace("23508882"," 2350 8882"))
        store.append(city1[i].replace("\uff0b","").replace(", Alberta","").replace(", MN 55425, ",""))
        store.append(state1[i].replace("\uff0b","").replace("Canada","AB"))
        store.append(zip1[i].replace("\uff0b",""))
        store.append(country_code[i].replace("\uff0b",""))
        store.append("<MISSING>")
        store.append(phone1[i].replace("\uff0b",""))
        store.append("<MISSING>")
        store.append(latitude[i])
        store.append(longitude[i])
        store.append(hours_of_operation[i].replace("\uff0b",""))
        store.append("<MISSING>")

        if "West Edmonton Mall" in store:
            store[6] = store[6].replace("<MISSING>","CA")
        if "Mall of America" in store:
            store[4] = store[4].replace("USA","MN")
            store[5] = store[5].replace("<MISSING>","55425")
            store[6] = store[6].replace("<MISSING>","US")
        if "Shop 2088, Level 2" in store or "SANLITUN" in store or "Mixc Shopping Mall" in store or "Via della Spiga" in store or "LONDON" in store or "ifc mall" in store or "SENDAGAYA" in store or "REGENT STREET" in store or "Harbour City Store" in store:
            pass
        else:
            # print(store)
            yield store
        

     
    # return return_main_object
    


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
