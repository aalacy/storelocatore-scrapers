from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('twistedtaco_com')



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
    p = 0
    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.twistedtaco.com/locations'
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")
    linklist= []
    hourlist = ['mon','tue','wed','thurs','sat','fri','sun','week','close','open','day','am','pm']
    divlist = soup.find('div',{'id':'1405153762'}).findAll('font')
    for div in divlist:
        try:
            title = div.find('a').text
            link = div.find('a')['href']
            flag = 0
            if link in linklist or link.find('coming-soon') > -1 or link.find('service') > -1 :
                flag = 1
            else:
                linklist.append(link) 
                link = 'https://www.twistedtaco.com'+ link                
                #logger.info(link)
                r = session.get(link, headers=headers, verify=False)
                soup = BeautifulSoup(r.text,'html.parser')
                det = soup.findAll('div',{'class':'dmNewParagraph'})
                title = soup.find('title').text
                try:
                    title = title.split(' |')[0].lstrip()
                except:
                    pass
                for dt in det:
                                       
                        
                    try:
                        if dt.text.find('Hours') > -1:
                            content = re.sub(cleanr,'\n',str(dt))
                            content = re.sub(pattern,'\n',content).split('\n')
                            #logger.info(content)
                            
                            ind = 0
                            phone = '<MISSING>'
                            hours = ''
                            street = ''
                            flag = 0
                            for i in range(0,len(content)):
                                
                                for t in hourlist:                                   
                                    if t in content[i].lower():
                                        flag = 1
                                        #logger.info(content[i])
                                        break
                                    
                                if  flag == 1:
                                    hours = hours + content[i] + ' '
                                    flag = 0
                                elif content[i].find(',') > -1:
                                    check = content[i].split(' ')[-1] 
                                    if (len(check.strip()) == 5  or len(check.strip()) == 4) and check.isdigit() :
                                        city,state  = content[i].split(', ')
                                        state,pcode = state.lstrip().split(' ')
                                        if len(pcode) == 4:
                                            pcode = '0' + pcode
                                    elif len(check.strip()) == 2 and not check.isdigit():
                                        city,state  = content[i].split(', ')
                                        pcode = '<MISSING>'
                                        
                                    else:
                                        street = street + content[i] + ' '
                                elif content[i].find('(') > -1 and content[i].find('-') > -1:
                                    phone = content[i]
                                elif content[i].lower().find('hour') > -1 or content[i].find('*') > -1:
                                    pass
                                else:
                                    street = street + content[i] + ' '
                                    
                                
                           
                           
                                
                            
                            if street.find('PH: ') > -1:
                                phone,street = street.split('PH: ')[1].split(' ',1)
                                try:
                                    hours,state = hours.split(', ')
                                    state,pcode = state.lstrip().split(' ',1)
                                    city = hours.split(' ')[-1]
                                    hours = hours.replace(city,'')
                                except:
                                    pass
                            if phone.find('*') > -1:
                                phone = '<MISSING>'

                            if hours == '' and city.strip() == 'Fargo':
                                hours = 'Summer hours: Monday - Friday: 10:30 am to 2:30 pm School year hours: Monday – Friday: 10:30 am to 9 pm'
                                
                            data.append([
                                'https://www.twistedtaco.com/locations',
                                link,                   
                                title,
                                street.strip().replace('Location:',''),
                                city.strip(),
                                state.strip(),
                                pcode.strip(),
                                'US',
                                "<MISSING>",
                                phone.strip().replace('– Fax',''),
                                '<MISSING>',
                                '<MISSING>',
                                '<MISSING>',
                                hours.replace('pm','pm ').strip()
                            ])
                            #logger.info(p,data[p])
                            p += 1
                            #input()
                            
                              
                           
                    except Exception as e:
                        logger.info(e)
                        pass

        except:
            pass
        
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
