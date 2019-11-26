import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import re

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)
#driver2 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver2 = webdriver.Chrome("chromedriver", options=options)


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    driver.get("view-source:https://www.topshop.com/store-locator?country=United+States")
    time.sleep(10)
    content2 = driver.page_source
    # Jvsc2 = content2[985591:1027655]
    Jvsc2 = content2.split('"stores":')[1].split(',"selectedStore"')[0]
    lis2 = json.loads(Jvsc2)

    driver2.get("view-source:https://www.topshop.com/store-locator?country=Canada")
    time.sleep(10)
    content = driver2.page_source
    # Jvsc = content[998614:1040627]
    Jvsc = content.split('"stores":')[1].split(',"selectedStore"')[0]
    lis1 = json.loads(Jvsc)

    data=[]
    
    main=lis1+lis2
    
    for i in range(len(main)):
        try:
            location_name=main[i]['name']
            if location_name =="":
                location_name = '<MISSING>'
        except:
            location_name='<MISSING>'
        try:
            street_addr=main[i]['address']['line1']+main[i]['address']['line2']
            if street_addr =="":
                street_addr = '<MISSING>'
        except:
            street_addr='<MISSING>'
        try:
            city=main[i]['address']['city']
            if city == "":
                city = '<MISSING>'
        except:
            city='<MISSING>'
        try:
            zipcode=main[i]['address']['postcode']
            if zipcode =="":
                zipcode = '<MISSING>'
            elif len(zipcode) == 4:
                zipcode = "0" + str(zipcode)
            elif len(zipcode) == 3:
                zipcode = "00" + str(zipcode)
        except:
            zipcode='<MISSING>'
        try:
            country=main[i]['address']['country']
            if country =="":
                country = '<MISSING>'
        except:
            country='<MISSING>'
        if country == 'United States':
            page_url = "https://www.topshop.com/store-locator?country=United+States"
            country = 'US'
        else:
            page_url = "https://www.topshop.com/store-locator?country=Canada"
            country = 'CA'
        try:
            op_hrs=str(main[i]['openingHours'])
            empty_hrs = bool(re.search(r'\d',op_hrs))
            if empty_hrs == False:
                op_hrs = '<MISSING>'
            else:
                op_hrs = op_hrs.replace("{","").replace("}","").replace("'","").replace(","," ")
        except:
            op_hrs='<MISSING>'
        try:
            store_number=main[i]['storeId']
            if store_number =="":
                store_number = '<MISSING>'
        except:
            store_number='<MISSING>'
        try:
            phno=main[i]['telephoneNumber'].replace("(+00)","").replace("(+001)","")
            if phno =="":
                phno = '<MISSING>'
        except:
            phno='<MISSING>'
        try:
            lng1=main[i]['longitude']
            if lng1 =="" or lng1 == 0:
                lng1 = '<MISSING>'
        except:
            lng1='<MISSING>'
        try:
            lat1=main[i]['latitude']
            if lat1 =="" or lat1 == 0:
                lat1 = '<MISSING>'
        except:
            lat1='<MISSING>'
        state='<MISSING>'
            
        data.append([
             'www.topshop.com',
             page_url,
             location_name,
             street_addr,
             city,
             state,
             zipcode,
             country,
             store_number,
             phno,
             '<MISSING>',
             lat1,
             lng1,
             op_hrs                     
           ])

    time.sleep(3)
    driver.quit()
    driver2.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
