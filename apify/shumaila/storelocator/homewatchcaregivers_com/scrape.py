# Import libraries
import requests
import time
from bs4 import BeautifulSoup
import csv
import string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('homewatchcaregivers_com')


session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-notifications") 
    chrome_path = 'c:\\Users\\Dell\\local\\chromedriver.exe'
    return webdriver.Chrome('chromedriver', chrome_options=options)

def fetch_data():   
    p = 0
   
    data = []
    statelist = []
    ment = []
    ment.append('none')
    driver = get_driver()
    url = 'https://www.homewatchcaregivers.com/locations/'
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")    
    repo_list = soup.find('select', {'id': 'LocationList_HDR0_State'})
    repo_list = repo_list.findAll('option')
    for rep in repo_list:
        statelist.append(rep.text.lower())        
     
    logger.info(len(statelist))
    for i in range(1,len(statelist)):
        state = statelist[i]
        state = state.replace(' ','-')
        statelink = 'https://www.homewatchcaregivers.com/locations/'+state
        #logger.info('state = ',i,statelist[i],statelink)
        try:
            count = 0
            page = 0
            #r1 = session.get(statelink, headers=headers, verify=False).text
            r1 = driver.get(statelink)
            mtrue = 0
            while True:
                if mtrue == 0:
                    #logger.info("MMMMMM")
                    r1  = driver.page_source
                    soup1 =BeautifulSoup(r1, "html.parser")
                    divlist = soup1.find('ul', {'class': 'state-list'})        
                    divlist = divlist.findAll('li')
                    try:
                        countdiv = soup1.find('div',{'class':'left flex'}).text
                        temp = countdiv[countdiv.find('of') + 2:len(countdiv)]
                        temp = temp.lstrip()
                        #logger.info(temp)
                        count = int(temp)
                        
                    except Exception as e:
                        #logger.info(e)
                        count = 1
                    #logger.info("COUNT = ",page,count)
                    if page == count:
                        break
                   # logger.info(countdiv)
                    #logger.info("len = ",len(divlist))
                    #input()
                    for div in divlist:           
                        lat = div['data-latitude']
                        longt = div['data-longitude']
                        det = div.find('h3')
                        title = det.text
                        link = det.find('a')['href']
                        title = title.replace('\n','')
                        if link.find('http') == -1:
                            link = 'https://www.homewatchcaregivers.com'+link
                            
                        #logger.info(link)
                        r2 = session.get(link, headers=headers, verify=False)        
                        soup2 =BeautifulSoup(r2.text, "html.parser")
                        try:
                            phone = soup2.find('span',{'itemprop':'telephone'}).text
                        except:
                            phone = "<MISSING>"
                        try:
                            street = soup2.find('span',{'itemprop':'streetAddress'}).text
                            street = street.replace('\t','')
                            street = street.replace('\n',' ')
                            street = street.strip()

                        except:
                            street = "<MISSING>"
                        try:
                            city = soup2.find('span',{'itemprop':'addressLocality'}).text
                            city = city.replace(',','')

                        except:
                            city = "<MISSING>"
                        try:
                            state = soup2.find('span',{'itemprop':'addressRegion'}).text

                        except:
                            state = "<MISSING>"
                        try:
                            pcode = soup2.find('span',{'itemprop':'postalCode'}).text

                        except:
                            pcode = "<MISSING>"
                        try:
                            hours = soup2.find('li',{'class':'item1'}).text
                            hours =hours.replace('\n','')
                            hours = hours.replace('Care','')
                            hours = hours.strip()
                            if hours.find('24-Hour') == -1:
                                hours = "<MISSING>"
                        except:
                            hours = "<MISSING>"

                        city = city.rstrip()
                        state = state.rstrip()
                        fflag = 0
                        for m in ment:
                            if m == title:
                                fflag = 1
                                break
                        if fflag == 0:
                            #logger.info("BBBB")
                            ment.append(title)
                            data.append([
                                        'https://www.homewatchcaregivers.com',
                                        link,                   
                                        title,
                                        street,
                                        city,
                                        state,
                                        pcode,
                                        'US',
                                        "<MISSING>",
                                        phone,
                                        "<MISSING>",
                                        lat,
                                        longt,
                                        hours
                                    ])
                            #logger.info(p,data[p])
                            p += 1
                        
                if count == 1:
                    page += 1
                if count > 1:
                    #logger.info("Enter")
                    try:
                        driver.find_element_by_xpath('/html/body/main/form/section/div/aside/div[2]/ul/li[2]/a').click()
                        mtrue = 0
                        page += 1
                              
                                # input()
                        time.sleep(2)
                    except Exception as e:
                        mtrue = 1
                        #logger.info("E!",e)
                    
                    
                


        except Exception as e:
            # broken link or no store
            #logger.info(e)
            pass










                
        
       
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
