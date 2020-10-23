import csv
from sgselenium import SgSelenium
import re
from bs4 import BeautifulSoup
from sgrequests import SgRequests
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('fastsigns_com')



driver = SgSelenium().chrome()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()
all=[]
def fetch_data():
    driver.get("https://www.fastsigns.com/worldwide")
    driver.find_element_by_xpath("//select[@name='DataTables_Table_0_length']/option[5]").click()

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    trs = soup.find_all('tr')
    del trs[0]
    for tr in trs:
        tds=tr.find_all('td')
        country = tds[-1].text.strip()
        if (country =="US" or country == "CA") and "coming soon" not in tds[0].text.lower():
            url=tds[0].find('a').get('href')
            if "https://www.fastsigns.com/" not in url:
                url="https://www.fastsigns.com/"+url
            logger.info(url)
            res= session.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            if "coming soon" in soup.find('div',{'class':'location-x'}).text.lower():
                continue
            loc = soup.find('h1',{'class':'title'}).text.strip()
            if loc =="":
                loc="<MISSING>"
            phone=soup.find('a',{'class':'phone'}).text.strip()

            addr=soup.find('div',{'class':'address'}).text.replace('VIEW MAP & DIRECTIONS','').replace(',','').strip()
            if country == "US":
                zip=re.findall(r'[0-9]{5}\-[\d]+', addr)
                if zip!=[]:
                    addr = addr.replace(zip[-1], '').strip()
                    zip = zip[-1].split('-')[0]

                else:
                    zip = re.findall(r'[0-9]{5}', addr)
                    if zip!=[]:
                        zip=zip[-1]
                        addr=addr.replace(zip,'').strip()
                        
                    else:
                        zip = re.findall(r'[0-9]{4}', addr.strip().split(" ")[-1])
                        if zip == []:
                           zip="<MISSING>"
                        else:
                            addr=addr.replace(zip[-1],'').strip()
                            zip="0"+zip[-1]

            else:
                zip = re.findall(r'[A-Z][0-9][A-Z] [0-9][A-Z][0-9]', addr)
                if zip == []:
                    zip=re.findall(r'[A-Z][0-9][A-Z][0-9][A-Z][0-9]', addr)
                    if zip !=[]:

                        addr = addr.replace(zip[-1], "").strip()
                        zip=zip[-1][:3]+" "+zip[-1][-3:]
                    else:
                        zip = "<MISSING>"
                else:
                    zip = zip[-1]
                    addr = addr.replace(zip, "").strip()

            state = re.findall(r'[A-Z]{2}', addr)
            if state == []:
                    state = "<MISSING>"
            else:
                    state = state[-1]
                    addr = addr.replace(state, "").strip()
            addr = addr.split("\n")
            city=addr[-1]
            del addr[-1]
            logger.info(zip)
            street=" ".join(addr)
            logger.info(street)
            #logger.info(soup.find('div',{'class':'address'}).find('a').get('href'))
            ll=soup.find('div',{'class':'address'}).find('a').get('href').strip().strip('/').split('/')[-1].split(',')
            #logger.info(ll)
            lat=ll[0]
            long=ll[1]
            #logger.info(ll)
            tim=soup.find('ul',{'class':'location-info'}).find_all('li')[-2].text.replace(' | ','').replace('\n',' ').strip()
            #logger.info()

            all.append([
                "https://www.fastsigns.com",
                loc,
                street,
                city,
                state,
                zip,
                country,
                url.strip().strip('/').split('/')[-1].split('-')[0],  # store #
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
