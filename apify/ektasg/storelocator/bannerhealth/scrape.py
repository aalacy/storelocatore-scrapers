
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import usaddress
import json
import pandas as pd

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon

def fetch_data():
    # Your scraper here
    data=[]
    driver.get("https://www.bannerhealth.com/locations/")
    time.sleep(10)
    
    text=driver.find_element_by_xpath("//div[@data-js='map_canvas_tab']").get_attribute('data-map-config')
    json_Data = json.loads(text)
    req_json=json_Data['markerList']
    df=pd.DataFrame(columns=['Latitude','Longitude','Address','Name','PhoneNumber'])
    for i in req_json:
        Lat=i['Latitude']
        Lon=i['Longitude']
        for j in i['Locations']:
            Add=j['Address']
            Name=j['Maps']
            if Name == '':
                Name=j['Name']
            PhNum=j['PhoneNumber']
            li=pd.DataFrame([[Lat,Lon,Add,Name,PhNum]],columns=['Latitude','Longitude','Address','Name','PhoneNumber'])
            df=df.append(li)
    df.reset_index(inplace=True,drop=True)
    driver.quit()
    for i in range(df.shape[0]):
        location_name = df.iloc[i]['Name'].split('/')[-1]
        raw_address =  df.iloc[i]['Address']
        street_addr = raw_address.split('<br/>')[0]
        if street_addr =='':
            street_addr = '<MISSING>'
        city = raw_address.split('<br/>')[1].split(',')[0]
        if city == '':
            city = '<MISSING>'
        zipcode = raw_address.split('<br/>')[1].split(',')[1].split(" ")[-1]
        state = raw_address.split('<br/>')[1].split(',')[1].split(" ")[-2]
        lat =  df.iloc[i]['Latitude']
        lon= df.iloc[i]['Longitude']
        phone =  df.iloc[i]['PhoneNumber']
        data.append([
             'https://www.bannerhealth.com/',
              location_name,
              street_addr,
              city,
              state,
              zipcode,
              'US',
              '<MISSING>',
              phone,
              '<MISSING>',
              lat,
              lon,
              '<MISSING>'
            ])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()



