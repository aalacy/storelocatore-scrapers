import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import time
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


driver = SgSelenium().chrome()
session = SgRequests()

all=[]
def fetch_data():
    # Your scraper here

    driver.get("https://www.zipsdrivein.com/locations/")
    stores = driver.find_element_by_class_name('sub-menu').find_elements_by_tag_name('a')
    hrefs=[]
    for store in stores:
        hrefs.append(store.get_attribute('href'))

    for url in hrefs:

        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        divs= soup.find_all('div',{'class':'wpgmaps_blist_row wpgmaps_odd'})
        divs+=soup.find_all('div',{'class':'wpgmaps_blist_row wpgmaps_even'})


        while True:
            if driver.find_elements_by_css_selector('[title="Next page"]')==[]:
                break

            driver.find_element_by_css_selector('[title="Next page"]').click()
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            divs += soup.find_all('div', {'class': 'wpgmaps_blist_row wpgmaps_odd'})
            divs += soup.find_all('div', {'class': 'wpgmaps_blist_row wpgmaps_even'})


        for div in divs:
            latlng= div.get('data-latlng').split(', ')
            lat=latlng[0]
            long=latlng[1]
            city='<MISSING>'
            add=div.get('data-address')
            addr=add.replace(', USA','')
            addr=addr.split(',')
            state=addr[-1].strip()
            del addr[-1]
            if ', USA' in add:
                city=addr[-1]
                del addr[-1]
            street = ', '.join(addr)
            loc=div.find('div', {'class': 'wpgmza-basic-list-item wpgmza_div_title'}).text.split(')')[1].strip()
            if city == '<MISSING>':
                city = loc

            all.append([
                "https://www.zipsdrivein.com/locations/",
                loc,
                street,
                city,
                state,
                '<MISSING>',
                'US',
                '<MISSING>',  # store #
                '<MISSING>',  # phone
                "<MISSING>",  # type
                lat,  # lat
                long,  # long
                '<MISSING>',  # timing
                url])

    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
