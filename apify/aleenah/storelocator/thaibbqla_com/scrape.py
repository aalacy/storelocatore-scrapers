import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('thaibbqla_com')



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

    res=session.get("https://thaibbqla.com/")
    soup = BeautifulSoup(res.text, 'html.parser')
    divs = soup.find_all('div', {'data-ux': 'Content'})

    for div in divs:
        loc = div.find('h4').text
        addr=div.find('p', {'data-ux': 'ContentText'}).text.strip().split(',')
        del addr[-1]
        sz=addr[-1].strip().split(' ')
        zip=sz[-1]
        del sz[-1]
        state= ' '.join(sz)
        del addr[-1]
        city=addr[-1]
        del addr[-1]
        street=' '.join(addr)
        phone = div.find_all('a', {'data-aid': 'CONTACT_INFO_PHONE_REND'})
        if phone==[]:
            phone="<MISSING>"
        else:

            phone = phone[0].text
        tim= div.find('div', {'data-aid': 'CONTACT_HOURS_CUST_MSG_REND'}).text.replace('pm','pm ').strip().replace(u'\xa0',u'')

        all.append([
            "https://thaibbqla.com/",
            loc,
            street,
            city,
            state.strip(),
            zip,
            "US",
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            tim,  # timing
            "https://thaibbqla.com/"])

    logger.info(all)
    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
