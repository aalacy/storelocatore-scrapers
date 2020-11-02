import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('aspencreekgrill_com')



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
all=[]
def fetch_data():
    # Your scraper here
    page_url=[]
    res=session.get("https://aspencreekgrill.com/")
    soup = BeautifulSoup(res.text, 'html.parser')
    urls = soup.find('ul', {'class': 'sub-menu'}).find_all('a')
    logger.info(len(urls))

    for url in urls:
        url=url.get('href')
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        loc = soup.find('div', {'class': 'et_pb_column et_pb_column_4_4 et_pb_column_inner et_pb_column_inner_0 et-last-child'}).find('h2').text
        divs=soup.find_all('div', {'class': 'et_pb_blurb_description'})
        tr=loc.lower().strip().split(" ")
        count=0
        for i in tr:
            tr[count]=i[0].upper()+i[1:]
            count+=1
        remove=' '.join(tr)
        city = remove
        addr=divs[0].text.replace("\n"," ").split(",")
        street =addr[0].replace(remove,"").strip()
        addr=addr[1].strip().split(" ")
        state = addr[0]
        zip=addr[1]
        tim=divs[1].text.replace("\n"," ").replace("pm","pm ").strip()
        phone=soup.find('a', {'class': 'et_pb_button et_pb_button_0 et_hover_enabled et_pb_bg_layout_dark'}).get('href').replace("tel:","").strip()
        if phone=="":
            phone=soup.find('h4', {'class': 'dsm-title et_pb_module_header'}).text
            phone = re.findall(r'[\d\-]+',phone)[0]
        all.append([
            "https://aspencreekgrill.com/",
            loc,
            street,
            city,
            state,
            zip,
            'US',
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            tim,  # timing
            url])
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
