from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('oggis_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_link = "https://oggis.com/locations/"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)

    try:
        base = BeautifulSoup(req.text,"lxml")
        logger.info("Got today page")
    except (BaseException):
        logger.info('[!] Error Occured. ')
        logger.info('[?] Check whether system is Online.')

    items = base.findAll('div', attrs={'class': 'post-entry post-entry-type-page post-entry-66'})
    items.pop(0)
    items.pop(0)
    
    data = []
    for item in items:
        no_zip = False
        locator_domain = "oggis.com"
        location_name = item.find('h3', attrs={'itemprop': 'headline'}).text.strip()
        raw_data = item.find('section', attrs={'class': 'av_textblock_section'}).text
        if raw_data[-1:] == "\n":
            raw_data = raw_data[:-1]
        raw_data = raw_data.split('\n')

        street_address = raw_data[0]
        bottom_line = raw_data[-1]
        city = bottom_line[:bottom_line.find(",")].strip()
        zip_code = bottom_line[bottom_line.rfind(" "):].strip()
        try:
            int(zip_code)
            state = bottom_line[bottom_line.find(",")+1:bottom_line.rfind(" ")].strip()
        except:
            zip_code = "<MISSING>"
            no_zip = True
            state = zip_code
        if state == "<MISSING>" and city == "Upland":
            state = "CA"
        country_code = "US"
        link = item.find('a')['href']
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        links = item.find('div', attrs={'class': 'result_links'})
        link = links.findAll('a')[0]['href']
        
        directions = links.findAll('a')[1]['href']
        latitude = directions[directions.rfind("=")+1:directions.rfind(",")].strip()
        longitude = directions[directions.rfind(",")+1:directions.rfind("(")].strip()
        comma_point = directions.find(",")
        if latitude == "":
            latitude = directions[directions.find("@")+1:comma_point].strip()
            longitude = directions[directions.find(",")+1:directions.rfind(",",comma_point)].strip()
            if longitude:
                if not latitude:
                    comma_point = longitude.rfind(",")
                    latitude = longitude[longitude.find("@")+1:comma_point].strip()
                    longitude = longitude[comma_point+1:].strip()                    
        
        if location_name == "Del Mar" and latitude == "32.7286969":
            # Set as missing since it is duplicated
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        
        phone = item.find('div', attrs={'class': 'result_address'})
        phone = phone.find('a').text

        hours_of_operation = ""
        check_hours = item.find_all(class_="av_textblock_section")[-1].text
        if "Operating Hours" in check_hours:
            hours_of_operation = check_hours.replace("\n"," ").replace("\r","").replace("*","").replace("<strong>","").replace("</strong>","").replace("<br>"," ").strip()
        else:
            req = session.get(link, headers = HEADERS)

            try:
                new_base = BeautifulSoup(req.text,"lxml")
                logger.info("Got store details page")
            except (BaseException):
                logger.info('[!] Error Occured. ')
                logger.info('[?] Check whether system is Online.')

            try:
                section = new_base.findAll('section', attrs={'class': 'av_textblock_section'})[1]
                hours_of_operation = section.find('div', attrs={'id': 'lbmb_hours'}).text.replace("\n"," ").replace("\r","").replace("*","")\
                .replace("<strong>","").replace("</strong>","").replace("<br>"," ").replace("Temporarily Closed  ","Temporarily Closed ").strip()
                
                if "  " in hours_of_operation:
                    hours_of_operation = hours_of_operation[:hours_of_operation.find("  ")].strip()
                
                if "Open 9:30am every" in hours_of_operation or "Open at" in hours_of_operation:
                    hours_of_operation = hours_of_operation[:hours_of_operation.find("Open")].strip()
                
                if "Breakfast" in hours_of_operation:
                    hours_of_operation = hours_of_operation[:hours_of_operation.find("Breakfast")].strip()
                
                if "NFL" in hours_of_operation:
                    hours_of_operation = hours_of_operation[:hours_of_operation.find("NFL")].strip()

            except:
                pass
        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        location_data = [locator_domain, base_link, location_name, street_address, city, state, zip_code,
                         country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
        location_data = [x for x in location_data]

        data.append(location_data)

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
