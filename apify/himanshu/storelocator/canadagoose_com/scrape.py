
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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://www.canadagoose.com/ca/en/find-a-retailer/find-a-retailer.html"
    r = requests.get(base_url)

    base_url1 = "https://hosted.where2getit.com/canadagoose/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E8949AAF8-550E-11DE-B2D5-479533A3DD35%3C%2Fappkey%3E%3Cgeoip%3E1%3C%2Fgeoip%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Corder%3Erank%3A%3Anumeric%2C_DISTANCE%3C%2Forder%3E%3Catleast%3E5%3C%2Fatleast%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3E%3C%2Faddressline%3E%3Clongitude%3E%3C%2Flongitude%3E%3Clatitude%3E%3C%2Flatitude%3E%3Ccountry%3E%3C%2Fcountry%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Csearchradius%3E10%7C25%7C50%7C100%7C250%3C%2Fsearchradius%3E%3Cradiusuom%3Emile%3C%2Fradiusuom%3E%3C%2Fformdata%3E%3C%2Frequest%3E"
    r1 = requests.get(base_url1)
    main_soup1 = BeautifulSoup(r1.text, "lxml")
    # print(main_soup1)


    n =  main_soup1.find_all("name")
    st = main_soup1.find_all("address1")
    city3 = main_soup1.find_all("city")
    lat = main_soup1.find_all("latitude")
    lon = main_soup1.find_all("longitude")
    phone3  = main_soup1.find_all("phone")
    state3 = main_soup1.find_all("state")
    postalcode3= main_soup1.find_all("postalcode")
    state3 = main_soup1.find_all("state")
    country =  main_soup1.find_all("country")

    # if len(postalcode3)==5:
    #     contry = "US"
    # else:
    #     contry = "CA"
    # print(main_soup1.find_all("state"))


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
                
                # print(i['href'])

            # latitude.append(i['href'].split('/@')[-1].split(",")[0])
            # longitude.append(i['href'].split('/@')[-1].split(",")[1])
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
        store.append(street_address1[i].replace("\uff0b",""))
        store.append(city1[i].replace("\uff0b",""))
        store.append(state1[i].replace("\uff0b",""))
        store.append(zip1[i].replace("\uff0b",""))
        store.append(country_code[i].replace("\uff0b",""))
        store.append("<MISSING>")
        store.append(phone1[i].replace("\uff0b",""))
        store.append("canadagoose")
        store.append(latitude[i])
        store.append(longitude[i])
        store.append(hours_of_operation[i].replace("\uff0b",""))
        # print(store)
        return_main_object.append(store)


    for i in range(len(st)):
        tem_var=[]
        tem_var.append("https://www.canadagoose.com")
        tem_var.append(n[i].text)
        tem_var.append(st[i].text)
        tem_var.append(city3[i].text)
        tem_var.append(state3[i].text)
        tem_var.append(postalcode3[i].text)
        tem_var.append(country[i].text)
        tem_var.append("<MISSING>")
        tem_var.append(phone3[i].text if phone3[i].text else "<MISSING>") 
        tem_var.append("canadagoose")
        tem_var.append(lat[i].text)
        tem_var.append(lon[i].text)
        tem_var.append("<MISSING>")
        # print(tem_var)
        return_main_object.append(tem_var) 

    return return_main_object


def scrape():
    data = fetch_data()

    write_output(data)


scrape()