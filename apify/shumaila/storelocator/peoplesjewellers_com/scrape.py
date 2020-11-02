from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('peoplesjewellers_com')



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
    p = 0
    cleanr = re.compile(r'<[^>]+>')    
    url = 'https://www.peoplesjewellers.com/store-finder/view-all-states'
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")   
    state_list = soup.find('div', {'id': '0'}).findAll('a')
    #logger.info(len(state_list))
    for slink in state_list:
        slink = 'https://www.peoplesjewellers.com/store-finder/' + slink['href']
        #logger.info(slink)
        r = session.get(slink, headers=headers, verify=False)    
        soup =BeautifulSoup(r.text, "html.parser")
        branchlist = soup.findAll('div',{'class':'viewstoreslist'})
        #logger.info(len(branchlist))
        pattern = re.compile(r'\s\s+')
        cleanr = re.compile(r'<[^>]+>')
        for branch in branchlist:
            #logger.info(branch.find('a')['href'])
            if branch.find('a')['href'].find('/null') == -1:
                link  = 'https://www.peoplesjewellers.com' + branch.find('a')['href']
                #logger.info(link)
                r = session.get(link, headers=headers, verify=False)    
                soup =BeautifulSoup(r.text, "html.parser")
                title = soup.find('h1',{'itemprop':'name'}).text
                street = soup.find('span',{'itemprop':'streetAddress'}).text
                city = soup.find('span',{'itemprop':'addressLocality'}).text
                state = soup.find('span',{'itemprop':'addressRegion'}).text
                pcode = soup.find('span',{'itemprop':'postalCode'}).text
                ccode = soup.find('span',{'itemprop':'addressCountry'}).text
                phone = soup.find('span',{'itemprop':'telephone'}).text
                coord = soup.find('a',{'class':'link-directions'})['href']
                lat, longt = coord.split('Location/')[1].split(',',1)            
                store = link.split('-peo')[1]
                soup = str(soup)
                hours = soup.split('detailSectionHeadline">Hours</div>')[1].split('{',1)[1].split('}',1)[0]
                hours = hours.replace('"','').replace('\n',' ').replace('::',' ')
                hours = re.sub(pattern,' ',hours).lstrip()
            else:               
                det = re.sub(cleanr, '\n',str(branch))
                det = re.sub(pattern,'\n',det).splitlines()
                #logger.info(det)
                i = 1
                title = det[i]
                i = i + 1
                street = det[i]
                i = i + 1
                state = ''
                try:
                    city,state = det[i].split(', ',1)
                    
                except:
                    street = street + ' ' + det[i]
                    i = i + 1
                    city,state = det[i].split(', ',1)

                state,pcode= state.lstrip().replace('\xa0',' ').split(' ',1)
                    
                i = i+ 1
                try:
                    phone = det[i]
                except:
                    phone = '<MISSING>'

                store = '<MISSING>'
                ccode = 'CA'
                lat = '<MISSING>'
                longt = '<MISSING>'
                hours = '<MISSING>'
                link =  '<MISSING>'  

            if len(pcode.replace(' ','')) > 7:
                temp,pcode = pcode.split(' ',1)
                state =state + ' ' + temp
                
                
            data.append([
                            'https://www.peoplesjewellers.com/',
                            link,                   
                            title,
                            street,
                            city,
                            state,
                            pcode,
                            ccode,
                            store,
                            phone,
                            '<MISSING>',
                            lat,
                            longt,
                            hours
                        ])
            #logger.info(p,data[p])
            p += 1

    
   
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
