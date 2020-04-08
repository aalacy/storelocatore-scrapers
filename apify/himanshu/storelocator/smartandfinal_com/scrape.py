import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import platform

system = platform.system()



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)



def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    if "linux" in system.lower():
        return webdriver.Firefox(executable_path='./geckodriver', options=options)
    else:
        return webdriver.Firefox(executable_path='geckodriver.exe', options=options)


def fetch_data():
    driver = get_driver()
    addresses =[]
    # store_name=[]
    # store_detail=[]
    # return_main_object=[]
    # "72fDQ9LH3Y3c9qx7w5uiDCxv75AOxMOxWQ"
    # "72fDQ9LH3Y3c9qx7w5uiDCxv75AOxMOxWQ-EWmzvkog"
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    #    "x-csrf-token": "aNQmu1EFjgrr_-4FO4dZtZDH3EmiL2Hjppjn6Xl3YKM",
    #    "accept": "application/json, text/plain, */*",
    #     "cookie":"__cfduid=d5896b654e4eed804006c5538ad7192d91576045548; has_js=1; session=1576045549030.018l903; _gat_UA-139304428-1=1; _gat_UA-65681409-5=1; _gat_UA-65681409-1=1; SESS04126c102d66b37b4b663fc1a54abd9a=72fDQ9LH3Y3c9qx7w5uiDCxv75AOxMOxWQ-EWmzvkog; XSRF-TOKEN=Y-sC_hrQXj_dPhgImbJUx3JKUM-Fg4MMBAHb-S3KypI; _ga=GA1.2.1907797409.1576045550; _gid=GA1.2.754341189.1576045550; _fbp=fb.1.1576045555516.20949364",
    #     # "cookie":"__cfduid=d8bc09f5764c85b3fee98c2a5d024aacf1576044172; has_js=1; SESS04126c102d66b37b4b663fc1a54abd9a=72fDQ9LH3Y3c9qx7w5uiDCxv75AOxMOxWQ-EWmzvkog; XSRF-TOKEN=p8t9qRPgZ5_sQ2L5_Xba33gkPanKjRE9rGCggOQdOhs; session=1576044175504.eap2zh6o; _gat_UA-139304428-1=1; _gat_UA-65681409-5=1; _gat_UA-65681409-1=1; _ga=GA1.2.997211385.1576044177; _gid=GA1.2.361799455.1576044177; _fbp=fb.1.1576044178547.920602647",
    # #    "cookie": "__cfduid=d35dc4740f258a8679a27188ebc6ee6411575872719; has_js=1; _ga=GA1.2.1612563966.1575872722; _gid=GA1.2.522272519.1575872722; SESS04126c102d66b37b4b663fc1a54abd9a=72fDQ9LH3Y3c9qx7w5uiDCxv75AOxMOxWQ-EWmzvkog; XSRF-TOKEN=aNQmu1EFjgrr_-4FO4dZtZDH3EmiL2Hjppjn6Xl3YKM; _fbp=fb.1.1575872728593.1119327461; session=1575955180720.dvfdcqa; _gat_UA-139304428-1=1; _gat_UA-65681409-5=1; _gat_UA-65681409-1=1"
    # #    "cookie": "__cfduid=d9a0d262a214ed25557c10cfdaa7409f71575955893; has_js=1; _ga=GA1.2.1612563966.1575872722; _gid=GA1.2.522272519.1575872722; SESS04126c102d66b37b4b663fc1a54abd9a=hemssx6cqt6tSdBgPO_d9lhDrcvGrCi5Xr7xP71_TEg; XSRF-TOKEN=QWmyzAHwKQ5O65ssbcSfZsF6DUxY8tqvKhymLCMqQ0M; _fbp=fb.1.1575955899702.1664016624; session=1575955897677.bo966d7p; _gat_UA-139304428-1=1; _gat_UA-65681409-5=1; _gat_UA-65681409-1=1"
    #     # "cookie": "__cfduid=d9a0d262a214ed25557c10cfdaa7409f71575955893; has_js=1; session=1575955897677.bo966d7p; SESS04126c102d66b37b4b663fc1a54abd9a=72fDQ9LH3Y3c9qx7w5uiDCxv75AOxMOxWQ-EWmzvkog; XSRF-TOKEN=QWmyzAHwKQ5O65ssbcSfZsF6DUxY8tqvKhymLCMqQ0M; _gat_UA-139304428-1=1; _gat_UA-65681409-5=1; _gat_UA-65681409-1=1; _ga=GA1.2.124037144.1575955900; _gid=GA1.2.1666361475.1575955900; _fbp=fb.1.1575955899702.1664016624",

    # }

    driver.get("https://www.smartandfinal.com/stores#/?coordinates=36.679107000000016,-121.64554999999996&zoom=0")
    s = SgRequests()
    cookies_list = driver.get_cookies()
# # print("cookies_list === " + str(cookies_list))
    cookies_json = {}
    for cookie in cookies_list:
        cookies_json[cookie['name']] = cookie['value']

    
    cookies_string = str(cookies_json).replace("{", "").replace("}", "").replace("'", "").replace(": ", "=").replace(
        ",", ";")

    cookies_string1 = cookies_string.split("SESS04126c102d66b37b4b663fc1a54abd9a")[0]+ 'SESS04126c102d66b37b4b663fc1a54abd9a=72fDQ9LH3Y3c9qx7w5uiDCxv75AOxMOxWQ-EWmzvkog;'+ ";".join(cookies_string.split("SESS04126c102d66b37b4b663fc1a54abd9a")[-1].split(";")[1:])
    # print(cookies_string1)


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
       "x-csrf-token": "aNQmu1EFjgrr_-4FO4dZtZDH3EmiL2Hjppjn6Xl3YKM",
       "accept": "application/json, text/plain, */*",
        "cookie": cookies_string1
   
    }
    # print("----------------cookies_string ",cookies_string)
    # for cookie in cookies:
    #     s.cookies.set(cookie['name'], cookie['value'])
    # # print("=============================data ",s.cookies)
    # soup = BeautifulSoup(driver.page_source, "lxml")
    data = s.get("https://www.smartandfinal.com/api/m_store_location?store_type_ids=1,2,3",headers=headers).json()
    # print(data)
    for loc in data['stores']:
        store_number =loc['store_number']
        location_type =''
        country_code =''
        hours_of_operation =''
        locator_domain ='https://www.smartandfinal.com/'
        phone =''
        dictionary ={}
        weekday = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
        for day,h in enumerate(loc['store_hours']):
            
            dictionary[weekday[day]] = h['open']+' '+h['close']
        hours_of_operation =''
        for h1 in dictionary:
            hours_of_operation = hours_of_operation+ ' ' +h1 + ' '+ dictionary[h1]
        
        
        phone = loc['phone']
        name = loc['storeName'].replace("-","").replace(".","")
        page_url = "https://www.smartandfinal.com/stores/"+str(name.replace(" ","-").lower())+"-"+str(store_number)+"/"+str(loc['locationID'])


        store = [locator_domain, loc['storeName'].capitalize(), loc['address'].capitalize(), loc['city'].capitalize(), loc['state'].capitalize(), loc['zip'], country_code,
                     store_number, phone, location_type, loc['latitude'], loc['longitude'], hours_of_operation, page_url]

        if str(store[2]) + str(store[-3]) not in addresses:
            addresses.append(str(store[2]) + str(store[-3]))

            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store
            # print("-----------------------------------",store)
    

def scrape():
    data = fetch_data()
    write_output(data)


scrape()


