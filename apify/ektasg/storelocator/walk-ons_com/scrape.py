import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
import re

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--disable-plugins")
options.add_argument( "--no-experiments")
options.add_argument( "--disk-cache-dir=null")

#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon

def fetch_data():
    data=[]
    driver.get("https://walk-ons.com/locations")
    time.sleep(5)
    street=abc=driver.find_elements_by_xpath("//div[@class='locationList collapse']//div[@class='row']//div[@class='locationItem col-md-6 text-left']//div[1]//div[2]")
    zipcode=driver.find_elements_by_xpath("//div[@class='locationList collapse']//div[@class='row']//div[@class='locationItem col-md-6 text-left']//div[1]//div[3]")
    ph=driver.find_elements_by_xpath("//div[@class='locationList collapse']//div[@class='row']//div[@class='locationItem col-md-6 text-left']//div[1]//div[4]")
    nam=driver.find_elements_by_xpath("//div[@class='locationList collapse']//div[@class='row']//div[@class='locationItem col-md-6 text-left']//div[1]//div[1]")
    loc=driver.find_elements_by_xpath("//div[@class='locationList collapse']//div[@class='row']//div[@class='locationItem col-md-6 text-left']//div[1]//div[5]/a")
    hou=driver.find_elements_by_xpath("//div[@class='locationList collapse']//div[@class='row']//div[@class='locationItem col-md-6 text-left']/child::div[2]")
    
    street1=[]
    zipco=[]
    city1=[]
    city2=[]
    phone1=[]
    name1=[]
    loca=[]
    hour1=[]

    for i in range(len(street)):
        street1.append(street[i].get_attribute("innerText").replace('\n','').replace('\t',''))
        zipco.append(zipcode[i].get_attribute("innerText").replace('\n','').replace('\t','').split(',')[1].split(' ')[2])
        city1.append(zipcode[i].get_attribute("innerText").replace('\n','').replace('\t','').split(',')[1].split(' ')[1])
        phone1.append(ph[i].get_attribute("innerText").replace('\n','').replace('\t',''))
        name1.append(nam[i].get_attribute("innerText").replace('\n','').replace('\t',''))
        city2.append(nam[i].get_attribute("innerText").replace('\n','').replace('\t','').split(',')[0])
        loca.append(loc[i].get_attribute('href'))
        hour1.append(hou[i].get_attribute('textContent').replace('\n','').replace('\t',''))
    dictn={'AL':'ALABAMA','FL':'FLORIDA','LA':'LOUISIANA','MS':'MISSISSIPPI','NC':'NORTH CAROLINA','TX':'TEXAS','AR':'Argentina','SC':'Seychelles'}    
    
    
 
    for k in range(32):
        street=street1[k]
        name=name1[k]
        city=city2[k]
        zipcode=zipco[k]
        state=city1[k]
        country='US'
        phone=phone1[k]
        hour=hour1[k]
        driver.get(loca[k])
        time.sleep(7)
        lat, lon = parse_geo(driver.current_url)
        data.append([
            'https://walk-ons.com',
            'https://walk-ons.com/locations',
            name,
            street,
            city,
            state,
            zipcode,
            country,
            '<MISSING>',
            phone,
            '<MISSING>',
            lat,
            lon,
            hour                     
           ])
        print(k)

    time.sleep(3)
    driver.quit()
    return data
         
def scrape():
        data = fetch_data()
        write_output(data)
    
scrape()        


         
         
         