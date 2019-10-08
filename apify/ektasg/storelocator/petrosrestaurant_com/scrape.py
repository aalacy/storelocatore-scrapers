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
    driver.get("https://www.petrosbrand.com/locations")
    li=[]
    abc=driver.find_elements_by_xpath("//ul[contains(@class,'mm-listview')]//a")
    for i in abc:
        k=i.get_attribute('href')
        li.append(k)
    li=[li[3],li[8],li[9],li[10],li[11],li[12]]
    hours=[]
    street=[]
    loc_name=[]
    geo_url1=[]
    phon=[]
    lati=['<MISSING>' for i in range(len(li))]
    lngi=['<MISSING>' for i in range(len(li))]
    for i in range(len(li)):
        driver.get(li[i])
        store_opening_hours=driver.find_element_by_xpath("//div[@class='text-box']/div[@class='field field--name-field-text field--type-text-long field--label-hidden field--item']").get_attribute("textContent")
        hours.append(store_opening_hours)
        location_name=driver.find_element_by_xpath('//h1[@class="page-header"]').get_attribute("textContent")
        street_address=driver.find_element_by_xpath("//div[@class='container']//p").get_attribute("textContent")
        street.append(street_address)
        loc_name.append(location_name)
        geomaps = driver.find_elements_by_xpath("//a[contains(@href,'//goo.gl/maps')]")
        geo_url = [geomaps[i].get_attribute('href') for i in range(0, len(geomaps))]
        geo_url1.append(geo_url)
        try:
            phone_no=driver.find_element_by_xpath("//div[@class='field field--name-field-text2 field--type-text-long field--label-hidden field--item']").get_attribute("textContent").replace("\t","").split()[-4]
        except:
            phone_no=driver.find_element_by_xpath("//div[@data-sr-id=9]").get_attribute("textContent").replace("\t","").split()[-4]
        phon.append(phone_no)
    for i in range(0, len(geo_url1)):
        print(i)
        driver2.get(geo_url1[i][0])
        time.sleep(10)
        lat, lon = parse_geo(driver2.current_url)
        lati[i] = lat
        lngi[i] = lon
    street[2]=street[2].replace('.',',')
    street[2]=street[2].replace('Beach',',')
    street[3]=street[3].replace('.',',')
    
    for i in range(len(li)):
        name=loc_name[i]
        street1=street[i].split(',')[0]
        state=street[i].split(',')[len(street[i].split(','))-1].split(" ")[1]
        zipcode=street[i].split(',')[len(street[i].split(','))-1].split(" ")[2]
        city=street[i].split(',')[len(street[i].split(','))-2]
        lat=lati[i]
        lng=lngi[i]
        hour=[hours[i].replace('\n',' ')]
        country='US'
        phone=phon[i]

        data.append([
            'www.petrosbrand.com',
            name,
            street1,
            city,
            state,
            zipcode,
            country,
            '<MISSING>',
            phone,
            '<MISSING>',
            lat,
            lng,
            hour                     
           ])

    time.sleep(3)
    driver2.quit()
    driver.quit()
    return data

         
def scrape():
        data = fetch_data()
        write_output(data)


scrape()