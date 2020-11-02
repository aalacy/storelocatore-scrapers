from bs4 import BeautifulSoup
import csv
import string
import re, time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('hotdogonastick_olo_com')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)



def fetch_data():
    data = []
    pattern = re.compile(r'\s\s+') 
    p = 0    
    url = 'https://hotdogonastick.olo.com/locations'    
    r = session.get(url, headers=headers, verify=False)  
    soup = BeautifulSoup(r.text, "html.parser")
    maindiv = soup.find('ul',{'id':'ParticipatingStates'})
    slinklist = maindiv.findAll('a')
    for statelink in slinklist:
        slink = 'https://hotdogonastick.olo.com' + statelink['href']
        r = session.get(slink, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        divlist = soup.findAll('li',{'class':'vcard'})
        for div in divlist:
            title = div.find('h2').text.replace('\r','').replace('\n','').strip()
            #logger.info(title)
            try:
                link = div.find('h2').find('a')['href']
            except:
                link = '<MISSING>'
            street = div.find('span',{'class':'street-address'}).text.replace('\r','').replace('\n','').strip()
            city = div.find('span',{'class':'locality'}).text.replace('\r','').replace('\n','').strip()
            state = div.find('span',{'class':'region'}).text.replace('\r','').replace('\n','').strip()
            phone = div.find('div',{'class':'location-tel-number'}).text.replace('\r','').replace('\n','').strip()
            hours = div.find('span',{'class':'location-hours'}).text.replace('\r','').replace('\n','').strip()
            hours = re.sub(pattern,' ',hours)
            lat = div.find('span',{'class':'latitude'}).find('span')['title']
            longt = div.find('span',{'class':'longitude'}).find('span')['title']
            data.append(['https://hotdogonastick.olo.com//',link,title,street,city,state,"<MISSING>",'US',"<MISSING>",phone,"<MISSING>",lat,longt,hours])
            #logger.info(p,data[p])
            p += 1
            
        
            
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
