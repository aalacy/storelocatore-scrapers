from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('loanmaxtitleloans_net')



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
    # Your scraper here
    data = []
    name =[]
    name.append('none')
    url = 'https://www.loanmaxtitleloans.net/Locations'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")   
    state_list = soup.findAll('li', {'class': 'state_item'})
   # logger.info("states = ",len(state_list))
    p = 0
    for states in state_list:
        states = states.find('a')
        #logger.info(states.text.strip())
        states = 'https://www.loanmaxtitleloans.net' + states['href']
        r = session.get(states, headers=headers, verify=False)
        ccode = 'US'
        soup = BeautifulSoup(r.text, "html.parser")
        city_list = soup.find('div', {'class': 'location_list_container second'}).findAll('a')

        #logger.info("cities = ",len(city_list))

        for cities in city_list:
            #cities = cities.find('a')
            #logger.info(cities.text.strip())
            cities = 'https://www.loanmaxtitleloans.net'+ cities['href']
            #logger.info(cities)
            r = session.get(cities, headers=headers, verify=False)
            
            soup = BeautifulSoup(r.text, "html.parser")
            branch_list = soup.findAll('div', {'id': 'nd_locationStores'})
            #logger.info(len(branch_list))
 
            for branch in branch_list:
                #logger.info(branch.text)
                branch = branch.find('a',{'class':'flex'})
                if branch['href'] == '':
                    pass
                else:
                    link = 'https://www.loanmaxtitleloans.net' +branch['href']
                    
                    #logger.info(link)
                    r = session.get(link, headers=headers, verify=False)    
                    
                    soup = BeautifulSoup(r.text, "html.parser")
                    street = soup.find('span',{'itemprop':'streetAddress'}).text
                    city = soup.find('span',{'itemprop':'addressLocality'}).text
                    state = soup.find('span',{'itemprop':'addressRegion'}).text
                    pcode = soup.find('span',{'itemprop':'postalCode'}).text
                    title = 'Loanmax - '+ city +', '+ state
                    phone = soup.find('span',{'itemprop':'telephone'}).text
                    hours = soup.find('div',{'class':'store_hours'}).text.replace('\n',' ')
                    if street in name:
                        pass
                    else:
                        name.append(street)
                        data.append(['https://www.loanmaxtitleloans.net',link,title,street,city,state,pcode,'US','<MISSING>',phone,'<MISSING>','<MISSING>','<MISSING>',hours])
                        #logger.info(p,data[p])
                        p += 1
                        

                
                
            
        
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
