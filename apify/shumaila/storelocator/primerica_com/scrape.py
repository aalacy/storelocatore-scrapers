
import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('primerica_com')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []    
    p = 0
    url = 'http://www.primerica.com/public/locations.html'
    page = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(page.text, "html.parser")
    maidiv = soup.find('main')
    mainsection = maidiv.findAll('section',{'class':'content locList'})
    #logger.info(len(mainsection))
    sec = 0
    while sec < 2:
        if sec == 0:
            ccode = "US"
        if sec == 1:
            ccode = "CA"
        rep_list = mainsection[sec].findAll('a')       
        cleanr = re.compile('<.*?>')
        pattern = re.compile(r'\s\s+')
        for rep in rep_list:            
            link = "http://www.primerica.com/public/" + rep['href']            
            #logger.info(link)           
            try:
               
                page1 = session.get(link, headers=headers, verify=False)                    
                time.sleep(1)
                soup1 = BeautifulSoup(page1.text, "html.parser")
                maindiv = soup1.find('main')
                xip_list = maindiv.findAll('a')
                logger.info("len = ",len(xip_list))
               
                for xip in xip_list:                    
                    try:
                        pcode = xip.text
                        #logger.info('http://www.primerica.com'+xip['href'])
                        page2 = session.get('http://www.primerica.com'+xip['href'], headers=headers, verify=False)                    
                        time.sleep(1)
                        soup2 = BeautifulSoup(page2.text, "html.parser")                   
                        mainul = soup2.find('ul',{'class':'agent-list'})
                        li_list = mainul.findAll('li')
                        #logger.info(len(li_list))
                        for m in range(0, len(li_list)):
                            try:
                                address = ''
                                alink = li_list[m].find('a')
                                
                                title = alink.text
                                alink = alink['href']                                
                                address =''
                                addrm  = ''
                                #logger.info(alink)
                                page3 = session.get(alink, headers=headers, verify=False)                    
                                time.sleep(2)
                                soup3 = BeautifulSoup(page3.text, "html.parser")                            
                                address = soup3.find('div',{'class':'officeInfoDataWidth'})
                                
                                cleanr = re.compile(r'<[^>]+>')
                               
                                address = cleanr.sub(' ', str(address))
                                #logger.info(address)
                                address = re.sub(pattern,'\n',address).lstrip()
                                address= address.splitlines()
                              
                                
                                city = ''
                                state = ''
                                i = 0
                                street = address[i]
                                i += 1
                                if address[i].find(',') == -1:
                                    street = street + ' ' +address[i]
                                    i += 1
                                else:
                                    city,state = address[i].split(', ')
                                   
                                
                                if address[i].find(',') > -1:
                                    city,state = address[i].split(', ')
                                    
                                i += 1
                                pcode = address[i]
                                if len(state) > 4:
                                    street  = address[0] +' '+ address[1]
                                    city, state = address[2].split(',',1)
                                    state = state.lstrip()
                                    pcode = address[3]
                                    
                                    
                                #logger.info(street, city,state,pcode)    
                                    
                               
                                
                                
                                phone = soup3.find('div',{'class':'telephoneLabel'}).text
                                phone = phone.replace('Office: ','')
                                phone = phone.replace("Mobile","")
                                phone = phone.replace(":","")
                                phone = phone.strip()
                                if len(phone) < 2:
                                    phone = "<MISSING>"
                                if len(street) < 2 :
                                    street = "<MISSING>"
                                if len(city) < 2:
                                    city  = "<MISSING>"                        
                                if len(state) < 2 :
                                    state = "<MISSING>"

                                if len(pcode) < 2:
                                    pcode = "<MISSING>"

                                if len(phone) < 11:
                                    phone = "<MISSING>"
                                i = 0
                                flag = True
                               
                                    
                                street = street.lstrip().replace(',','')
                                city = city.lstrip().replace(',','')
                                state = state.lstrip().replace(',','')
                                pcode = pcode.lstrip().replace(',','').rstrip()
                                try:
                                    for i in range(0,len(data)):                                        
                                        #logger.info(i, pcode,data[i][6])
                                        if alink == data[i][1] and title == data[i][2]:
                                            #logger.info("exist")
                                            flag = False
                                            break
                                    
                                except Exception as e:
                                    logger.info(e)
                                if pcode.find('-') == -1 and sec == 0 and pcode != '<MISSING>' and len(pcode) > 6 :
                                    pcode = pcode[0:5] + '-' +pcode[5:len(pcode)]

                               
                                if state == "NF":
                                    state = "NL"
                                if state == "PQ":
                                    
                                    state = "QC"
                                if flag:
                                    data.append([
                                            'http://www.primerica.com/',
                                            alink,
                                            title,
                                            street,
                                            city,
                                            state,
                                            pcode.rstrip(),
                                            ccode,
                                            "<MISSING>",
                                            phone,
                                            "<MISSING>",
                                            "<MISSING>",
                                            "<MISSING>",
                                            "<MISSING>",
                                        ])
                                    
                                #logger.info(street,city,state,pcode,phone)
                                    #logger.info(p,data[p])
                                    p += 1
                                    #input()
                                #input()
                                
                            except Exception as e:
                                logger.info(e)
                                pass
                               
                    except Exception as e:
                        logger.info(e)
                        pass
                        


                    #break
            except Exception as e:
                logger.info(e)
                pass

            #driver1.quit()
            #break
        sec += 1
        #if sec == 1:
            #break

    return data




def scrape():

    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
