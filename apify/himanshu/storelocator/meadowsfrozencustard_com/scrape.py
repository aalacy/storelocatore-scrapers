import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('meadowsfrozencustard_com')




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
    store_name = []
    return_main_object = []
    address1 = []
    page_url = 'http://meadowsfrozencustard.com/columns/'
    r = session.get(page_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
        
    k  = soup.find('div', {'class': 'page-content'}).find_all('div', {'class': 'col-lg-3'})

    for i in k:

        li = i.find('h3')
        if li ==None:
            pass
        else:
            tem_var =[]
            location_name = li.text
            # logger.info(location_name)
            try:
                address_tmp =i.find_all('p')[1]
                address1 = i.find_all('p')[1].text.strip().split(',')
            except:
                address_tmp =i.find_all('p')[0]
                address1 = i.find_all('p')[0].text.strip().split(',')
            if(len(address1)==3):
                address = address1[0]
                city = address1[1]
                state_tmp = address1[2].split(' ')
                if(len(state_tmp)==3):
                    state = state_tmp[1]
                    zip = state_tmp[2]
                if(len(state_tmp)==4):
                    state = state_tmp[1]+' '+ state_tmp[2]
                    zip = state_tmp[3]
                if(len(state_tmp)==5):
                    state = state_tmp[1]+' '+ state_tmp[2]+' '+ state_tmp[3]
                    zip = state_tmp[4]
              
                
            elif(len(address1)==1):
                address_tmp = address1[0].split(' ')
                address = address_tmp[0]+' '+address_tmp[1]+' '+address_tmp[2]+' '+address_tmp[3]
                city = address_tmp[4]
                state = address_tmp[5]
                zip = address_tmp[6]
                
            elif(len(address1)==2):
                address= address1[1]
                city_tmp = address_tmp.find_next_sibling("div").text.split(',')
                city = city_tmp[0]
                state_tmp = city_tmp[1].split(' ')
                state = state_tmp[1]
                zip = state_tmp[2]
                
            elif(len(address1)==4):
                address = address1[1]
                city = address1[2]
                state_tmp = address1[3].split(' ')
                state = state_tmp[1]
                zip =state_tmp[2]

            if len(zip) < 5:
                zip = "0" + zip
                
            link = i.find('a')['href']
            if "new-alexandria" in link:
                link = "https://meadowsfrozencustard.com/columns/new-alexandria/"
            r1 = session.get(link, headers=headers)
            soup1 = BeautifulSoup(r1.text, "lxml")
            phone1 = soup1.find_all('div', {'class': 'contact-info'})
            hour1 =  soup1.find('div', {'class': 'about-location'})
            hour2 = list(hour1.stripped_strings)
            if len(hour2) < 2:
                hour1 =  soup1.find_all('div', {'class': 'about-location'})[1]
                hour2 = list(hour1.stripped_strings)

            if "hollidaysburg" in link:
                try:
                    hour1 =  phone1
                    hour2 = list(hour1[0].stripped_strings)
                except:
                    pass

            hour = ""
            for line in hour2:
                if "pm" in line.lower() or ":00" in line.lower() or ":30" in line.lower() or ": closed" in line.lower() or "OPEN DAILY" in line.upper():
                    hour = (hour + " " + line.replace("–","-").replace("Hours:","Daily:")).strip()
            if "Open Daily" in hour:
                hour = hour[hour.find("Open Daily"):hour.rfind("pm")+2].strip()
            if "(" in hour:
                hour = hour[:hour.find("(")].strip()
            if "P.M" in hour:
                hour = hour[:hour.rfind("P.M")+3].strip()
            if "PM" in hour:
                hour = hour[:hour.rfind("PM")+2].strip()
            if "Fall" in hour:
                hour = hour[:hour.find("Fall")].strip()
            if not hour:
                hour = '<MISSING>'
                
            # .replace('Contact InformationPhone: 908-393-2928','<MISSING>')
                
            if(len(phone1)==2):
                phone1 = soup1.find_all('div', {'class': 'contact-info'})[1].text.strip().replace('Contact Information','').replace('Phone:','').replace('Hours: 10AM – 11PM','')
                phone = phone1.replace('Address: 715 Gateway Center Blvd Grovetown GA 30813','<MISSING>').replace("Map of our location","").strip()
                if not phone:
                    phone = '<MISSING>'
            elif len(phone1)==1:
                phone1 = soup1.find_all('div', {'class': 'contact-info'})[0].text.strip().replace('Contact Information','').replace('Phone:','').replace('Hours: 10AM – 11PM','')
                phone = phone1.replace('Address: 715 Gateway Center Blvd Grovetown GA 30813','<MISSING>').replace("Map of our location","").strip()
            else:
                phone = '<MISSING>'
            if not phone:
                phone = '<MISSING>'
        
            try:
                map_link = soup1.iframe["src"]
                lat_pos = map_link.rfind("!3d")
                latitude = map_link[lat_pos+3:map_link.find("!",lat_pos+5)].strip()
                lng_pos = map_link.find("!2d")
                longitude = map_link[lng_pos+3:map_link.find("!",lng_pos+5)].strip()
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            tem_var.append('http://meadowsfrozencustard.com/')
            tem_var.append(location_name)
            tem_var.append(address)
            tem_var.append(city.strip())
            tem_var.append(state) 
            tem_var.append(zip)
            tem_var.append('US')
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append(latitude)
            tem_var.append(longitude)
            tem_var.append(hour)
            tem_var.append(link)
            if "Canberra" in tem_var:
                pass
            else:
                return_main_object.append(tem_var)
                   
 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
