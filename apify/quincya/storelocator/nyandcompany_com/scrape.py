import csv
from sgrequests import SgRequests
from sgselenium import SgChrome

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    session = SgRequests()

    driver = SgChrome().chrome()
    driver.get("https://www.nyandcompany.com/locations/")

    raw_page = driver.page_source
    sessconf = raw_page.split('_dynSessConf"')[1].split('">')[0].split('="')[-1]

    cookies = driver.get_cookies()
    cookie= ""
    for cook in cookies:
        cookie = cookie + cook["name"] + "=" + cook["value"] + "; "

    cookie = cookie.strip()[:-1]

    HEADERS = {
            'authority': 'www.nyandcompany.com',
            'method': 'GET',
            'path': '/locations/?_DARGS=/storelocator/storelocator.jsp.1&_dyncharset=UTF-8&_dynSessConf=' + sessconf + '&%2Fcom%2Fnyco%2FApplicationConfig.storelocatorLat.homeSite=39&_D%3A%2Fcom%2Fnyco%2FApplicationConfig.storelocatorLat.homeSite=+&%2Fcom%2Fnyco%2FApplicationConfig.storelocatorLng.homeSite=-96&_D%3A%2Fcom%2Fnyco%2FApplicationConfig.storelocatorLng.homeSite=+&location_type=-1&%2Fcom%2Fnyco%2Fstore%2Fcommerce%2FStoreLocatorFormHandler.distance=10000&_D%3A%2Fcom%2Fnyco%2Fstore%2Fcommerce%2FStoreLocatorFormHandler.distance=+&%2Fcom%2Fnyco%2Fstore%2Fcommerce%2FStoreLocatorFormHandler.storeType=-1&_D%3A%2Fcom%2Fnyco%2Fstore%2Fcommerce%2FStoreLocatorFormHandler.storeType=+&addressLat=40.7388319&_D%3AaddressLat=+&addressLng=-73.98153370000001&_D%3AaddressLng=+&addressStatus=OK&_D%3AaddressStatus=+&submit=submit&_D%3Asubmit=+&_DARGS=%2Fstorelocator%2Fstorelocator.jsp.1',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'content-length': '275',
            'cache-control': 'max-age=0',
            'cookie': cookie,
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
        }

    data = []
    found = []

    locator_domain = "nyandcompany.com"
    for i in ["0","1","-1"]:
        if i == '0':
            location_type = "NY&C Stores"
        elif i == '1':
            location_type = "NY&C Outlets"
        else:
            continue

        base_link = 'https://www.nyandcompany.com/locations/?_DARGS=/storelocator/storelocator.jsp.1&_dyncharset=UTF-8&_dynSessConf=' + sessconf + '&%2Fcom%2Fnyco%2FApplicationConfig.storelocatorLat.homeSite=39&_D%3A%2Fcom%2Fnyco%2FApplicationConfig.storelocatorLat.homeSite=+&%2Fcom%2Fnyco%2FApplicationConfig.storelocatorLng.homeSite=-96&_D%3A%2Fcom%2Fnyco%2FApplicationConfig.storelocatorLng.homeSite=+&location_type=' + str(i) + '&%2Fcom%2Fnyco%2Fstore%2Fcommerce%2FStoreLocatorFormHandler.distance=10000&_D%3A%2Fcom%2Fnyco%2Fstore%2Fcommerce%2FStoreLocatorFormHandler.distance=+&%2Fcom%2Fnyco%2Fstore%2Fcommerce%2FStoreLocatorFormHandler.storeType='+ str(i) +'&_D%3A%2Fcom%2Fnyco%2Fstore%2Fcommerce%2FStoreLocatorFormHandler.storeType=+&addressLat=40.7388319&_D%3AaddressLat=+&addressLng=-73.98153370000001&_D%3AaddressLng=+&addressStatus=OK&_D%3AaddressStatus=+&submit=submit&_D%3Asubmit=+&_DARGS=%2Fstorelocator%2Fstorelocator.jsp.1'

        stores = session.get(base_link, headers = HEADERS).json()['stores']

        for store in stores:
            store_number = store["StoreID"]
            if store_number in found:
                continue
            found.append(store_number)
            location_name = store["storeName"]
            street_address = store["StreetAddress"]
            city = store["City"]
            state = store["State"]
            zip_code = store["postalCode"]
            if len(zip_code) > 5:
                continue
            country_code = "US"
            phone = store["PhoneNumber"]
            latitude = store["latitude"]
            longitude = store["longitude"]
            link = "https://www.nyandcompany.com/locations/%s/%s" %(state.lower(),location_name.replace(" ","-").lower().replace("(","%28").replace(")","%29"))
            hours_of_operation = (store["dayHour1"] + " " + store["dayHour2"] + " " + store["dayHour3"] + " " + store["dayHour4"] + " " + store["dayHour5"] + " " + store["dayHour6"] + " " + store["dayHour7"]).replace("_closed - closed", " Closed").replace("_", " ")

            # Store data
            data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    driver.close()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
