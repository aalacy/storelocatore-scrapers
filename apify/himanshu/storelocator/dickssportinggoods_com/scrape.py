import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import unicodedata
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('dickssportinggoods_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    return_main_object = []
    try:
        r = session.get("https://storelocator.dickssportinggoods.com/responsive/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E17E8F19C-098E-11E7-AC2C-11ACF3F4F7A7%3C%2Fappkey%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Catleast%3E6%3C%2Fatleast%3E%3Climit%3E10000%3C%2Flimit%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3Enew+york%3C%2Faddressline%3E%3Ccountry%3E%3C%2Fcountry%3E%3Clongitude%3E%3C%2Flongitude%3E%3Clatitude%3E%3C%2Flatitude%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Csearchradius%3E5000%3C%2Fsearchradius%3E%3Cwhere%3E%3Cbrandname%3E%3Ceq%3EDicks+Sporting+Goods%3C%2Feq%3E%3C%2Fbrandname%3E%3Cflag3%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fflag3%3E%3Cflag4%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fflag4%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E",headers=headers)
    except:
        pass
    soup = BeautifulSoup(r.text,"lxml")
    for location in soup.find_all("poi"):
        # logger.info(location)
        name = location.find("name").text.strip()
        address = ""
        city = ""
        state = ""
        postalcode = ""
        if location.find("address1"):
            address = address + location.find("address1").text.strip()
        # if location.find("address2"):
        #     address = address + location.find("address2").text.strip()
        if location.find("city"):
            city = city + location.find("city").text.strip()
        if location.find("state"):
            state = state + location.find("state").text.strip()
        if location.find("postalcode"):
            postalcode = postalcode + location.find("postalcode").text.strip()
        latitude = ""
        if location.find("latitude"):
            latitude = latitude + location.find("latitude").text.strip()
        longitude = ""
        if location.find("longitude"):
            longitude = longitude + location.find("longitude").text.strip()
        phone = ""
        if location.find("phone"):
            phone = phone + location.find("phone").text.strip()
        store_id = location.find("clientkey").text.strip()
        store = []
        store.append("https://www.dickssportinggoods.com")
        store.append(name)
        store.append(address if address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(postalcode if postalcode else "<MISSING>")
        store.append(location.find("country").text.strip())
        if store[-1] != "CA" and store[-1] != "US":
            continue
        store.append(store_id)
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        page_url = "https://stores.dickssportinggoods.com/" + store[4].lower() + "/" + str(store_id)
        page_request = session.get(page_url,headers=headers)
        page_soup = BeautifulSoup(page_request.text,"lxml")
        hour_tmp =page_soup.find("div",{"class":"hours-wrapper"})
        # logger.info(hour_tmp)
        # hours = " ".join(list(page_soup.find("div",{"class":"hours-wrapper"}).stripped_strings))
        if hour_tmp !=None:

            hours= " ".join(list(page_soup.find("div",{"class":"hours-wrapper"}).stripped_strings))
        else:
            hours ='<MISSING>'
        store.append(hours.replace("Store Hours ","") if hours else"<MISSING>")
        store.append(page_url)
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
