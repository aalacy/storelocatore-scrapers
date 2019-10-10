import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

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


driver.get("https://www.zehrs.ca/store-locator?icta=store-locator")
time.sleep(20)
driver.find_element_by_xpath("//button[@title='Zoom out']").click()
time.sleep(40)

text_len=driver.find_elements_by_xpath("(//div[contains(@class,'list-item__button-details')])")
store_df=pd.DataFrame()
store_df["store_name"]=["" for i in range(len(text_len))]
store_df["street_name"]=["" for i in range(len(text_len))]
store_df["city_postal_address"]=["" for i in range(len(text_len))]
store_df["store_opening_hours"]=["" for i in range(len(text_len))]
store_df["phone_no"]=["" for i in range(len(text_len))]
store_df["store_address"]=["" for i in range(len(text_len))]
store_df["lattitude"]=["" for i in range(len(text_len))]
store_df["longitude"]=["" for i in range(len(text_len))]
store_df["store_address"]=["" for i in range(len(text_len))]

def fetch_data():
# Your scraper here
    for i in range(len(text_len)):
        print (i)
        href_driver=driver.find_element_by_xpath("(//a[contains(@aria-label,'Store Details')])["+str(i+1)+"] ").get_attribute("href")
        driver2.get(href_driver)
        time.sleep(5)
    
        store_df["store_opening_hours"][i]=driver2.find_element_by_xpath("(//div[contains(@class,'hours-section__weekly-hours-group hours-')]) ").get_attribute("textContent").replace('\t','').replace('\n','')
        store_df["phone_no"][i]=driver2.find_element_by_xpath("(//p[contains(@class,'store-information__content')]) ").get_attribute("textContent").replace('\t','').replace('\n','').replace("'",'')
    
        store_df["store_address"][i]=driver.find_element_by_xpath("(//div[contains(@class,'list-item__button-details')])["+str(i+1)+"]/p[contains(@class,'list-item__address address')] ").get_attribute("textContent")
        store_df["street_name"][i]=driver.find_element_by_xpath("(//span[contains(@class,'address__street-address')])["+str(i+1)+"] ").get_attribute("textContent")
        store_df["store_name"][i]=driver.find_element_by_xpath("(//h1[contains(@class,'list-item__store-name')])["+str(i+1)+"] ").get_attribute("textContent")
        store_df["city_postal_address"][i]=driver.find_element_by_xpath("(//span[contains(@class,'address__city-postal-code')])["+str(i+1)+"] ").get_attribute("textContent")
        store_df["City"]=store_df["store_name"]
      
          
    data=[]  
    for i in range(len(store_df)):
        data.append([
             '"https://www.zehrs.ca/',
              store_df.iloc[i]['store_name'],
              store_df.iloc[i]['street_name'],
              store_df.iloc[i]['City'],
              store_df.iloc[i]['city_postal_address'].split(",")[1].split(" ")[1],
              store_df.iloc[i]['city_postal_address'].split(" ")[2]+" "+store_df.iloc[i]['city_postal_address'].split(" ")[3],
              'CA',
              '<MISSING>',
              store_df.iloc[i]['phone_no'],
              '<MISSING>',
              '<MISSING>',
              '<MISSING>',
              store_df.iloc[i]['store_opening_hours']
            ])
    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
driver.quit()
driver2.quit()