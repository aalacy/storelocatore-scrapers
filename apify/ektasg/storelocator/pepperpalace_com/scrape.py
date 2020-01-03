import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import usaddress
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

#driver=webdriver.Chrome('C:\chromedriver.exe', options=options)
driver = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
    driver.get("https://pepperpalace.com/pages/store-locations/")
    time.sleep(10)
    wait = WebDriverWait(driver, 20)
    element = wait.until(expected_conditions.presence_of_element_located((By.XPATH, 
                                                                          "//a[@title='Close'][contains(@class,'fancy')]")))
    close_popup = driver.find_element_by_xpath("//a[@title='Close'][contains(@class,'fancy')]")
    close_popup.click()
    time.sleep(5)
    data=[]
    locationelements_1=driver.find_elements_by_xpath("//h4//a")
    locationele=list(filter(lambda x: (not(x.text == '')) , locationelements_1))
    locationURLs=[i.get_attribute('href') for i in locationele]
    locationText=[i.text  for i in locationele]
    canadaElements=len(driver.find_elements_by_xpath("//h4[preceding-sibling::p]//a"))
    count=0
    fullcontent=[]
    for i in locationURLs:
        driver.get(i)   
        text=driver.find_element_by_xpath("//meta[@name='description']").get_attribute('content') 
        fullcontent.append(text)
        count=count+1
        print(count)
    for store in range(len(fullcontent)):        
        loc_name_splitter=re.search(r'\d+', fullcontent[store]).group()
    
        location_name = fullcontent[store].split(loc_name_splitter)[0]
        location_name=location_name.strip()
        if(location_name==''):
            location_name=locationText[store]
        if('Â' in location_name):
            location_name=location_name.replace('Â','')
        city = locationText[store].lower()
        if('(' in fullcontent[store]):
            phno='('+fullcontent[store].split('(')[1]
            alphabet='abcdefghijklmnopqrstuvwxyz@.!â€‹Â'
            phno=phno.lower()
            for letter in alphabet:
                phno = phno.replace(letter, '')
                if('  ' in phno):
                    phno=phno.strip()
                    phno=phno.split("  ")[0]
                phno=[v for v in phno if v in '1234567890- ()']
                str1=""
                phno=str1.join(phno)
            raw_address = fullcontent[store].split('(')[0]
        else:
            phno='<MISSING>'
            raw_address = fullcontent[store]
        if(location_name in raw_address):
            raw_address=raw_address.replace(location_name,"").replace("pepperpalacemallga@gmail.com","")
        #print(raw_address)
        if store>=len(fullcontent)-canadaElements:
            country='CA'
        else:
            country='US'
        """try:
            tagged = usaddress.tag(raw_address)[0]
        except:
            pass
        try:
            zipcode = tagged['ZipCode']
            if('pepper' in zipcode):
                zipcode=zipcode.split('pepper')[0]
            zipcode=''.join(e for e in zipcode if e.isalnum())
            if(len(zipcode)<5):
                zipcode=" ".join(raw_address.split(" ")[-2:])
            raw_address=raw_address.replace(zipcode,'')
        except:
            zipcode=raw_address.split(" ")[-1]
            if(len(zipcode)<5):
                zipcode=" ".join(raw_address.split(" ")[-2:])
            if(len(zipcode)>10):
                zipcode='<MISSING>'
            raw_address=raw_address.replace(zipcode,'')
            pass
        
        try:
            tagged = usaddress.tag(raw_address)[0]
        except:
            pass    
        if(city.split(" ")[0].lower() in raw_address.lower()):
            splitter= raw_address.lower().index(city.split(" ")[0].lower())
            street_addr=raw_address[0:splitter]
        else:
            try:
                street_addr=raw_address.split(tagged['PlaceName'])[0]
            except:
                try:
                    street_addr=raw_address.split(tagged['StateName'])[0]
                except:
                    street_addr=raw_address
        if(len(street_addr)<10):
            splitter= raw_address.lower().split(city.split(" ")[0].lower())
            street_addr="".join(raw_address[:-1])
        raw_address=raw_address.replace(street_addr,"")
        try:
            tagged = usaddress.tag(raw_address)[0]
        except:
            pass
        try:
            state = tagged['StateName'].split(',')[1]
            city = tagged['PlaceName'] + " " + tagged['StateName'].split(',')[0]
    
        except:
            try:
                state = tagged['StateName']
                city = tagged['PlaceName']
            except:
                pass
        if('pepper' in state):
            state=state.split('pepper')[0]
        if "Pepper Palace Niagara Falls" in location_name:
            zipcode = 'L2G 3W6'"""
        #raw_address=raw_address.decode('utf-8').replace(u"​\u200b","").encode('utf-8')
        addr=raw_address.replace(u"​\u2022","").strip().split(",")
        sz=addr[-1].strip()
        state=sz.split(" ")[0]
        zipcode = sz.replace(state,"").strip()
        addr=raw_address.replace(sz,"").strip()
        cit=re.findall(r'[0-9A-Za-z\.]([A-Z][a-z]+)',addr)
        if cit != []:
          city=cit[-1]+addr.split(cit[-1])[-1].replace(",","")
          #print(cit)
        else:
          city=addr.split(" ")[-1].replace(",","")
          #print("!!!!!!!!!!!!!!!!!!!!!!!1!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        street_addr=addr.replace(city,"").strip()

        #print(street_addr)
        #print(city)
        #print(state)
        #print(zipcode)
        #print("*******************************")
        data.append([
             'https://pepperpalace.com/',
             locationURLs[store],
             location_name,
             street_addr,
             city,
             state,
             zipcode,
             country,
             '<MISSING>',
             phno,
             '<MISSING>',
             '<MISSING>',
             '<MISSING>',
             '<MISSING>'                     
           ])

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
