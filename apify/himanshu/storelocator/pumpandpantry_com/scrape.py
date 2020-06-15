import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    locator_domain = 'https://pumpandpantry.com/location-list/' 
    to_scrape = locator_domain
    page = session.get(to_scrape)
    soup = BeautifulSoup(page.content, 'html.parser')
    stores = soup.find_all('div', {'class': 'panel-grid panel-has-style'})
    hours_arr = []
    for st in stores:
        store_number= list(st.stripped_strings)[0]
        street_address = list(st.stripped_strings)[1]
        city = list(st.stripped_strings)[2].split(",")[0]
        state = list(st.stripped_strings)[2].split(",")[1].strip()
        zip_code = list(st.stripped_strings)[2].split(",")[2]
        phone = list(st.stripped_strings)[3]
        hours_arr = list(st.stripped_strings)[4]
        page_url = st.find("a")['href']
        soup1 = BeautifulSoup(session.get(page_url).text, 'html.parser')
        hours1 = " ".join(list(soup1.find(lambda tag: (tag.name == "h3" or tag.name == "h2") and "HOURS" in  tag.text.strip()).find_next("div",{'class':"siteorigin-widget-tinymce textwidget"}).stripped_strings))
        name = soup1.find("div",{"class":"sow-headline-container"}).text.strip()
        tag_phone = soup1.find(lambda tag: (tag.name == "script") and "store_locator_options" in tag.text.strip()).text.split("store_locator_options =")[1].replace("/* ]]> */",'').replace("};",'}')
        country_code = 'US'
        location_type = '<MISSING>'
        lat = json.loads(tag_phone)['mapDefaultLat']
        long = json.loads(tag_phone)['mapDefaultLng']
        hours = '<MISSING>'
        store_data = ["https://pumpandpantry.com/", name, street_address, city, state, zip_code, country_code,
                     store_number.replace("#",''), phone, location_type, lat, long, hours1,page_url]
        yield store_data   
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
