import csv
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup as bs
import time
import requests
from sgselenium import SgSelenium



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
    addresses = []
    driver = SgSelenium().chrome()
    driver.get("https://kwiktrip.com/Maps-Downloads/Store-List")
    
    locator_domain = "https://kwiktrip.com"
    hours_of_operation ="<MISSING>"
    while True:
        soup = BeautifulSoup(driver.page_source,"lxml")
        for data in soup.find_all("tbody",{"class":"row-hover"}):
            for tr in data.find_all("tr"):
                store_number = list(tr.stripped_strings)[0]
                page_url="https://www.kwiktrip.com/locator/store?id="+str(store_number)
                payload = {}
                headers = {
                'Referer': 'https://www.kwiktrip.com/Maps-Downloads/Store-List',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
                }
                response = requests.get(page_url,headers=headers,data = payload)
                if response.status_code==200:
                    if response != None:
                        soup1 = BeautifulSoup(response.text,'lxml')
                        h = soup1.find("div",{"class":"Store__dailyHours"})
                        if h != None:
                            hours_of_operation =  " ".join(list(h.stripped_strings))
                    
                        h = soup1.find("div",{"class":"Store__open24Hours"})
                        if h != None:                   
                            hours_of_operation = " ".join(list(h.stripped_strings))
                else:
                    hours_of_operation="<MISSING>"
                page_url = "https://www.kwiktrip.com/locator/store?id="+str(store_number)
                location_name = list(tr.stripped_strings)[1]
                street_address = list(tr.stripped_strings)[2]
                city = list(tr.stripped_strings)[3]
                state = list(tr.stripped_strings)[4]
                zipp = list(tr.stripped_strings)[5]
                phone = list(tr.stripped_strings)[6]
                latitude = list(tr.stripped_strings)[7].replace("-93.22204",'<MISSING>').replace("Yes",'<MISSING>')
                longitude = list(tr.stripped_strings)[8]
                if "Yes" in latitude or "Yes" in longitude:
                    latitude="<MISSING>"
                    longitude="<MISSING>"
                location_type = "<MISSING>"
                country_code = "US"
                store =[]
                hours_of_operation1=''
                if hours_of_operation.strip():
                    hours_of_operation1= hours_of_operation
                else:
                    hours_of_operation1 = "<MISSING>"
                
                if "1208 W 13TH ST" in street_address:
                    phone="(319) 472-3591"
                    latitude="42.15902"
                    longitude = "-92.03876"
                if "https://www.kwiktrip.com/locator/store?id=589" in page_url:
                    phone="<MISSING>"
                    latitude="42.03466"
                    longitude = "-91.54563"
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation1, page_url]
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                # print("~~~~~~~~~~~~~~~~~~~~~~  ",store)
                yield store
        soup1 = BeautifulSoup(driver.page_source,"lxml")
        if soup1.find("a",{"id":"tablepress-4_next"}):
            driver.find_element_by_xpath("//a[@id='tablepress-4_next']").click()
        else:
            break
        if soup1.find("a",{"class":"paginate_button current"}).text=="15":
            driver.quit()
            break
   

   

def scrape():
    data = fetch_data()
    write_output(data)


scrape()


