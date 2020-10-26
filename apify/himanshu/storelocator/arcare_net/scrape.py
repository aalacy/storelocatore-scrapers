import csv
from bs4 import BeautifulSoup
from sgselenium import SgSelenium


def write_output(data):
    with open('data.csv', mode='w', newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    locator_domain = base_url = "https://www.arcare.net/"
    driver = SgSelenium().firefox()
    driver.get("https://www.arcare.net/locations/")
    soup = BeautifulSoup(driver.page_source, "lxml")


    for key, value in enumerate(soup.find_all('div',{'class':'results_wrapper'})):
        location_name =  value.find('span',{'class':'location_name'}).text.strip()

        street_address = value.find('span',{'class':'slp_result_street'}).text.strip()

        city = value.find('span',{'class':'slp_result_citystatezip'}).text.strip().split(',')[0].strip()
        state = value.find('span', {'class': 'slp_result_citystatezip'}).text.strip().split(',')[1].strip().split(' ')[0].strip()
        zipp = value.find('span', {'class': 'slp_result_citystatezip'}).text.strip().split(',')[1].strip().split(' ')[1].strip()
        phone = value.find('span', {'class': 'slp_result_phone'}).text.strip()


        latitude ='<MISSING>'
        longitude = '<MISSING>'
        country_code = "US"
        store_number = '<MISSING>'

        location_type = '<MISSING>'
        hours_of_operation = value.find('span', {'class': 'slp_result_hours'}).text.replace('Hours:','').strip()
        if hours_of_operation == '':
            hours_of_operation = '<MISSING>'

        page_url = value.find('a', {'class': 'storelocatorlink'})['href']
        
        street_address = street_address.lower().replace('suite', '').replace('floor', '').capitalize()
        if "11219 financial centre parkway,  200" in street_address:
            street_address = street_address.replace(",  200",'')
        if "501 millwood circle,  e" in street_address:
            street_address = street_address.replace(",  e",'')
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",store)
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
