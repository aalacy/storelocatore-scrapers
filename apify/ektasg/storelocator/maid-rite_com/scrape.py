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
#driver2 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver2 = webdriver.Chrome("chromedriver", options=options)

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
    data=[]
    driver.get("http://maid-rite.com/locations.php")
    time.sleep(10)
    name=driver.find_elements_by_xpath("//tbody//tr//td[contains(@class,'1')]")
    name1=driver.find_elements_by_xpath("//tbody//tr//td[contains(@class,'2')]")
    
    place=[]
    elements =[]
    str = 'append'
    count = 0
    for j in name:
        place.append(j.text)
        elements.append(j)
    for j in name1:
        place.append(j.text)
        elements.append(j)
    for i in range(len(place)):
        place[i]=place[i].split('\n')       
        if(len(place[i])==6):
            location_name = place[i][0]
            if (place[i][1] == 'TEMPORARILY CLOSED'):
                str = 'pass'
            else:
                street_address = place[i][1] + " " + place[i][2]
                city = place[i][3].split(",")[0]
                state = place[i][3].split(",")[1].split(" ")[1]
                zipcode = place[i][3].split(",")[1].split(" ")[2]
                phone = place[i][4]
                geomap = elements[i].find_element_by_css_selector('a').get_attribute('href')
                driver2.get(geomap)
                latitude, longitude = parse_geo(driver2.current_url)
                str = 'append'
        elif(len(place[i])==5):
            if (place[i][1] == 'TEMPORARILY CLOSED'):
                str = 'pass'
            else:
                location_name = place[i][0]
                street_address = place[i][1]
                city = place[i][2].split(",")[0]
                state = place[i][2].split(",")[1].split(" ")[1]
                zipcode = place[i][2].split(",")[1].split(" ")[2]
                phone = place[i][3]
                geomap = elements[i].find_element_by_css_selector('a').get_attribute('href')
                driver2.get(geomap)
                latitude, longitude = parse_geo(driver2.current_url)
                str = 'append'
        elif(len(place[i])==4):
            location_name = place[i][0]
            street_address = place[i][1]
            city = place[i][2].split(",")[0]
            state = place[i][2].split(",")[1].split(" ")[1]
            zipcode = place[i][2].split(",")[1].split(" ")[2]
            phone = place[i][3]
            latitude = '<MISSING>'
            longitude = '<MISSING>'
            str = 'append'

        country='US'
        hours_of_operation='<MISSING>'
        if str == 'append':
            data.append([
                 'http://maid-rite.com/',
                 location_name,
                 street_address,
                 city,
                 state,
                 zipcode,
                 country,
                 '<MISSING>',
                 phone,
                 '<MISSING>',
                 latitude,
                 longitude,
                 hours_of_operation
               ])
        count+=1
        print(count)

    time.sleep(5)
    driver.quit()
    driver2.quit()
    return data                   
                                
def scrape():
        data = fetch_data()
        write_output(data)
    
scrape()        




