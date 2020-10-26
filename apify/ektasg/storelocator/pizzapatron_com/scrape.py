import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
import re
import pandas as pd
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('pizzapatron_com')



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
    driver.delete_all_cookies()
    driver.get("https://order.pizzapatron.com/locations/")
    time.sleep(10)
    main_df=pd.DataFrame(columns=['location_name', 'street_address', 'city', 'country_code', 'phone',
           'latitude', 'longitude', 'hours_of_operation', 'locator_domain',
           'store_number', 'location_type', 'state', 'zip'])
    list_url=[]
    k=driver.find_elements_by_xpath("//ul[@id='ParticipatingStates']//a")
    for j in k:
        list_url.append(j.get_attribute('href')) 
        
    for x in list_url:
        driver.get(x)
        l1=driver.find_elements_by_xpath("//li[contains(@class,'vcard')]//div[contains(@class,'location-tel-number')]")
        l1=pd.DataFrame([i.text for i in l1],columns={'phone'})
        
        l2=driver.find_elements_by_xpath("//li[contains(@class,'vcard')]//span[contains(@class,'location-hours')]")
        l2=pd.DataFrame([i.text for i in l2],columns={'hours_of_operation'})
        
        l3=driver.find_elements_by_xpath("//li[contains(@class,'vcard')]//span[contains(@class,'street-address')]")
        l3=pd.DataFrame([i.text for i in l3],columns={'street_address'})
        
        l4=driver.find_elements_by_xpath("//li[contains(@class,'vcard')]//span[contains(@class,'locality')]")
        l4=pd.DataFrame([i.text for i in l4],columns={'city'})
        
        l5=driver.find_elements_by_xpath("//li[contains(@class,'vcard')]//span[contains(@class,'geo')]//span[contains(@class,'latitude')]/span")
        l5=pd.DataFrame([i.get_attribute('title') for i in l5],columns={'latitude'})
        
        l6=driver.find_elements_by_xpath("//li[contains(@class,'vcard')]//span[contains(@class,'geo')]//span[contains(@class,'longitude')]/span")
        l6=pd.DataFrame([i.get_attribute('title') for i in l6],columns={'longitude'})
        
        l7=driver.find_elements_by_xpath("//span[contains(@class,'fn org')]")
        l7=pd.DataFrame([i.text for i in l7],columns={'location_name'})
        
        l8=driver.find_elements_by_xpath("//span[contains(@class,'region')]")
        l8=pd.DataFrame([i.text for i in l8],columns={'state'})
        
        temp_url=[]
        l9=[]
        k=driver.find_elements_by_xpath("//ul[contains(@id,'ParticipatingRestaurants')]//a[contains(@href,'http')]")
        for j in k:
            temp_url.append(j.get_attribute('href')) 

        for i in temp_url:
            driver.get(i)
            k=driver.find_element_by_xpath("//span[contains(@class,'postal-code')]").text
            l9.append(k)
        
        l9=pd.DataFrame(l9,columns={'zip'})
        df=pd.concat([l7,l3,l4,l8,l1,l5,l6,l2,l9],axis=1)
      
        
        
        df['locator_domain']='https://www.pizzapatron.com/'
        df['store_number']='<MISSING>'
        df['location_type']='<MISSING>'
        df['country_code']='US'
        #df['zip']='<MISSING>'
        main_df=main_df.append(df)       
    main_df['country_code']='US'    
    count=0    
    for i in range(len(main_df)):
        data.append([
             main_df.iloc[i]['locator_domain'],
              main_df.iloc[i]['location_name'],
              main_df.iloc[i]['street_address'],
              main_df.iloc[i]['city'],
              main_df.iloc[i]['state'],
              main_df.iloc[i]['zip'],
              main_df.iloc[i]['country_code'],
              main_df.iloc[i]['store_number'],
              main_df.iloc[i]['phone'],
              main_df.iloc[i]['location_type'],
              main_df.iloc[i]['latitude'],
              main_df.iloc[i]['longitude'],
              main_df.iloc[i]['hours_of_operation']
            ])
        count=count+1
        logger.info(count)
    return data
    

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
driver.quit()    
