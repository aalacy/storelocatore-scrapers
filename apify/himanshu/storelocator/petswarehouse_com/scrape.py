import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('petswarehouse_com')



session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",",quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # logger.info("data::" + str(data))
        for i in data or []:
            writer.writerow(i)
def fetch_data():

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    
    locator_domain = "https://www.petswarehouse.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    hours = "<MISSING>"
    page_url = ''

    soup = BeautifulSoup(session.get("https://app.mapply.net/front-end/iframe.php?api_key=mapply.f277a6be14a42a337f26caeda97c8791").text,'lxml')
    for data in soup.find(lambda tag:(tag.name == "script") and "markersCoords.push" in tag.text).text.split("markersCoords.push(")[1:-2]:
        data = json.loads(re.sub(r'\s+'," ",re.sub("(\w+):", r'"\1":',re.sub("'",'"',html.unescape(data.split(");")[0]))).replace('="',"='").replace('">',"'>").replace('Kohl"s',"Kohl's'").replace('Wendy"s',"Wendy's")))
        
        lat = data['lat']
        lng = data['lng']
        store_number = data['id']
        location_detail = BeautifulSoup(data['address'],"lxml")

        location_name = location_detail.find("span",{"class":"name"}).text.strip()
        street_address = location_detail.find("span",{"class":"address"}).text.strip()
        city = location_detail.find("span",{"class":"city"}).text.strip()
        state = location_detail.find("span",{"class":"prov_state"}).text.strip()
        zipp = location_detail.find("span",{"class":"postal_zip"}).text.strip()
        phone = location_detail.find("span",{"class":"phone"}).text.strip()
        hours = location_detail.find("span",{"class":"hours"}).text.strip()
        page_url = "https://www.petswarehouse.com/store-locator/"

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
        store_number, phone, location_type, lat, lng, hours, page_url]
        store = [str(x) if str(x).strip() else "<MISSING>" for x in store]
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
