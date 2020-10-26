import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sgselenium import SgSelenium
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('happyspizza_com')



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
    headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.happyspizza.com',
        'Referer': 'https://www.happyspizza.com/locations/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'}
    #res=session.get("https://www.happyspizza.com/locations/",headers=headers)
    #soup = BeautifulSoup(res.text, 'html.parser')
    driver.get("https://www.happyspizza.com/locations/")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    sa = soup.find_all('div', {'class': 'col-5 my-lg-3'})
    #logger.info(soup)
    for a in sa:
        url=a.find('a').get('href')
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        logger.info(url)
        try:

            loc=soup.find('h1', {'class': 'hp-gradienttxt mt-3 mt-lg-5'}).text
        except:
            """all.append([
                "https://www.happyspizza.com",
                "<INACCESSIBLE>",
                "<INACCESSIBLE>",
                "<INACCESSIBLE>",
                "<INACCESSIBLE>",
                "<INACCESSIBLE>",
                "<INACCESSIBLE>",
                "<INACCESSIBLE>",  # store #
                "<INACCESSIBLE>",  # phone
                "<INACCESSIBLE>",  # type
                "<INACCESSIBLE>",  # lat
                "<INACCESSIBLE>",  # long
                "<INACCESSIBLE>",  # timing
                url])"""
            continue
        addr=soup.find('p', {'class': 'hp-storeaddress hp-black mb-1'}).text.strip().split('\n')
        street=addr[0]
        addr=addr[1].strip().split(',')
        city=addr[0]
        addr=addr[1].strip().split(' ')
        state=addr[0]
        zip=addr[1]
        phone=soup.find('p', {'class': 'hp-cherry mb-lg-1 mt-3 mb-3'}).text.replace('Phone','').strip()
        tim=soup.find_all('div', {'class': 'row no-gutters'})[1].text.replace('am','am ').replace('pm','pm ').replace('day:','day: ').replace('  ',' ')
        #logger.info(tim)
        iframes=soup.find_all('iframe')
        if iframes==[]:
            lat=long="<MISSING>"
        else:
            lat,long=re.findall(r'!1d[\d]+(-?\d{2}\.[\d]+)!2d(-?[\d\.]+)',iframes[0].get('src'))[0]

        all.append([
            "https://www.happyspizza.com",
            loc,
            street,
            city,
            state,
            zip,
            "US",
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            lat,  # lat
            long,  # long
            tim.strip(),  # timing
            url])
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
