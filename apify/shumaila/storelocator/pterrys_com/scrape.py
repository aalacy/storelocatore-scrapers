# Import libraries
import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time, usaddress
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('pterrys_com')




def get_driver():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-notifications")   
   
    return webdriver.Chrome('C:\\Users\\Dell\\local\\chromedriver.exe', chrome_options=options)



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url",  "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)
            

def fetch_data():
    # Your scraper here
    data = []
    p = 0
    url = 'https://pterrys.com/locations'
    page = requests.get(url)
    
    soup = BeautifulSoup(page.text, "html.parser")
   
    repo_list = soup.findAll('div',{'class':'itemImg'})
    
   

    for link in repo_list:
        link = link.find('a')
        link = "https://pterrys.com"+link['href']
        page = requests.get(link)
        soup = BeautifulSoup(page.text, "html.parser")
        maindiv = soup.find('div',{'class':'itemsCollectionContent'})
        title = soup.find('title').text
        start = title.find("-")
        title = title[0:start]
        try:
            ltype = soup.find('div',{'class':'blockInnerContent'}).text
        except:
            ltype = "<MISSING>"
        div_list = maindiv.findAll('div',{'class':'item'})
        
        detail = div_list[0]
        li_list = detail.findAll('li')
        street = li_list[0].text
        state = li_list[1].text
        address = street + " " + state
        address = address.replace('Get Directions','')
        logger.info(address)
        address = usaddress.parse(address)
        logger.info(address)
        
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if temp[1].find("Address") != -1 or temp[1].find("Occupancy") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or temp[1].find("Building") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                "USPSBoxID") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1
        


        street = street.lstrip()
        city = city.lstrip()
        city = city.replace(",", "")
        street = street.replace(",", "")
        state = state.replace(",", "")
        if city.find("Building H ") > -1:
            city = city.replace("Building H ","")
            street = street + ' Building H'

        state = state.lstrip()
        pcode = pcode.lstrip()

    
        detail = div_list[1]
        hours = ""
        li_list = detail.findAll('li')
        for hdetail in li_list:
            hours = hours + " " + hdetail.text
        '''try:
           hours = hours + " |" + detail.find('p').text
        except:
            pass'''

        #hours = hours[3:len(hours)]
        hours = hours.lstrip().replace('am',' am ').replace('pm',' pm ').replace('Break',' Break').replace('  ',' ')
        #logger.info(hours)
       
        detail = div_list[2]
        phone = detail.find('li').text
        start = phone.find(' ')
        if start != -1:
            phone = phone[0:start]
        #logger.info(phone)
        if len(phone)< 3:
            phone = "<MISSING>"
        if len(street)< 3:
            street = "<MISSING>"
        if len(city) < 3:
            city = "<MISSING>"
        if len(state) < 2:
            state = "<MISSING>"
        if len(pcode) < 3:
            pcode = "<MISSING>"
        
        #logger.info("...........................")

        data.append([
            'https://pterrys.com',
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
            "<MISSING>",
            "<MISSING>",
            hours
        ])
        #logger.info(p,data[p])
        p = p + 1

    return data         
        
 
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
