import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgselenium import SgSelenium
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ontherun_com')




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


session = SgRequests()
driver = SgSelenium().chrome()
all=[]

def fetch_data():
    # Your scraper here


    #
    driver.get("https://www.ontherun.com/store-locator/")


    tag=driver.find_element_by_tag_name('body').find_elements_by_tag_name('script')[1]
    stores=re.findall(r'locations = (\[[^;]+)',tag.get_attribute('text').replace('\n','').replace('            ','').replace('        ','').replace('    ','').replace('\'','').replace(',},','},').replace(',]',']'))[0].split('},{')

    logger.info(len(stores))

    for store in stores:
        id,lat,long,url=re.findall(r'store_number: (.*),lat: (.*),lon: (.*),status:.*<a href="([^"]+)">',store)[0]
        #logger.info(id, lat, long, url)

        url='https://www.ontherun.com/store-locator/'+url
        logger.info(url)

        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        street,city,state,zip=re.findall(r'<h1>(.*)<br/>(.*), (.*), ([\d]+)</h1>',str(soup))[0]
        phone=re.findall(r'phone-number">([\(\)\d \-]+)</h4>',str(soup))
        if phone==[]:
            phone="<MISSING>"
        else:
            phone=phone[0]

        logger.info(street,city,state,zip,phone)
        tim=soup.find('div',{'class':'weekdays columns small-20'}).text.strip().replace('\n\n',',').replace('\n',' ')

        logger.info(tim)

        all.append([

            "https://www.ontherun.com",
            '<MISSING>',
            street.replace('amp;',''),
            city,
            state,
            zip,
            "US",
            id,  # store #
            phone,  # phone
            "<MISSING>",  # type
            lat,  # lat
            long,  # long
            tim,  # timing
            url])



    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()