import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('loveforpilates_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])

        # logger.info("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    store_detail = []
    
    lat = []
    lng=[]
    return_main_object = []
    address1 = []
    base_url ='https://loveforpilates.com'
     
    

    
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    main =  soup.find_all('ul', {'class': 'dropdown-menu'})[1].find_all('li')
    for i in main:
        link = i.find('a')['href']
        r1 = session.get(link, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        main1 =  soup1.find_all('div', {'class': 'span6'})[1]
              

   
        location_name =(list(main1.stripped_strings))[1]
        address_tmp = (list(main1.stripped_strings))[3].split(',')   
        phone =  (list(main1.stripped_strings))[5]    
        hour1 = (list(main1.stripped_strings))[-15:]  
        hour = " ".join(hour1).replace('|','').replace('Hours','').strip()         
        if(len(address_tmp)==5):
            address =address_tmp[0]+' '+address_tmp[1]
            city = address_tmp[2]
            state = address_tmp[3]
        elif(len(address_tmp)==4):
            address =address_tmp[0]
            city = address_tmp[1]
            state = address_tmp[2]
             
 
   
      
        tem_var =[]
    
        tem_var.append(base_url)
        tem_var.append(location_name)
        tem_var.append(address)
        tem_var.append(city)
        tem_var.append(state) 
        tem_var.append('<MISSING>')
        tem_var.append('US')
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hour)
        tem_var.append(link) 
       

        return_main_object.append(tem_var)
        
           
 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
