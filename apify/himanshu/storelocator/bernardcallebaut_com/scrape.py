import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
# import sgzip
# import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bernardcallebaut_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []



    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        "accept": "application/json, text/javascript, */*; q=0.01",
        # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    locator_domain = "https://bernardcallebaut.com"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"



    r= session.get('https://cococochocolatiers.com/pages/locations',headers = headers)
    soup = BeautifulSoup(r.text,'html.parser')
    for url in soup.find('div',class_='PageContent PageContent--narrow Rte').find_all('h5'):
        loc_url = url.a['href']
        # logger.info(page_url)
        if "United States" == url.text:
            country_code = "US"
        else:
            country_code = "CA"
        page_url= loc_url
        r_loc= session.get(loc_url,headers = headers)
        soup_loc = BeautifulSoup(r_loc.text,'lxml')
        try:
            div = soup_loc.find('div',class_='easyslider-contents')
            for info in div.find_all('div',class_='easyslider-item'):
                l_name = info.find('div',class_='easyslider-header').text.strip()
                # city = location_name[0].split('/')[1].split(',')[0]
                # state = location_name[0].split('/')[1].split(',')[-1]
                # logger.info(location_name)
                content = info.find('div',class_='easyslider-content')
                for details in content.find_all('p'):
                    list_details = list(details.stripped_strings)
                    list_details = [el.replace('\xa0',' ') for el in list_details]
                    if "Location" in " ".join(list_details):
                       list_details.remove('Location')
                    if len(list_details) ==5:
                        street_address = list_details[0].split(',')[0].strip()
                        city = list_details[0].split(',')[-1].split()[0].strip()
                        state  = list_details[0].split(',')[-1].split()[1].strip()
                        zipp = " ".join(list_details[0].split(',')[-1].split()[2:]).strip()
                        location_name  = city
                        phone =re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_details[1]))[0]
                        hours_of_operation = " ".join(list_details[3:]).strip()
                        # logger.info(street_address+" | "+city+" | "+state+" | "+zipp+" | "+location_name+" | "+phone+" | "+hours_of_operation)
                    elif len(list_details) ==6:
                        tag_address = list_details[0].split(',')
                        if len(tag_address) >2:
                            street_address = tag_address[0] + " "+tag_address[1]
                        else:
                            street_address = tag_address[0].strip()
                        csz = tag_address[-1].split()
                        if len(csz) == 2:
                            city = csz[0].strip()
                            state = csz[-1].strip()
                            zipp = "<MISSING>"
                        elif  len(csz) == 3:
                            city = csz[0] + " "+csz[1]
                            state = csz[-1].strip()
                            zipp= "<MISSING>"
                        else:
                            city = csz[0].strip()
                            state = csz[1]
                            zipp= " ".join(csz[2:]).strip()
                        location_name = city
                        phone = list_details[2].strip()
                        hours_of_operation = ",".join(list_details[4:]).strip()
                        # logger.info(street_address+" | "+city+" | "+state+" | "+zipp+" | "+location_name+" | "+phone+" | "+hours_of_operation)
                    elif len(list_details) ==7:

                        if "Domestic Terminal, Pre-security" in " ".join(list_details):
                            list_details.remove('Domestic Terminal, Pre-security')
                        if "Departures Level" in " ".join(list_details):
                            list_details.remove('Departures Level – Gate A, Calgary International Airport')

                        # logger.info(list_details)
                        # logger.info(len(list_details))
                        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                        tag_address = " ".join(list_details[:2]).strip().replace('Phone','').split(',')
                        if "Southcentre Mall" in tag_address[0]:
                            tag_address.remove('Southcentre Mall')
                        if len(tag_address) == 1:
                            l_name = info.find('div',class_='easyslider-header').text.strip()

                            city = l_name.split('/')[1].split(',')[0].strip()
                            state = l_name.split('/')[1].split(',')[-1].strip()


                            zipp = "<MISSING>"
                            # logger.info(zipp)
                            location_name = city
                            street_address = tag_address[0]




                        elif len(tag_address) ==2:
                            street_address = tag_address[0].strip()
                            city  = tag_address[-1].split()[0].strip()
                            state = tag_address[-1].split()[1].strip()
                            zipp=" ".join(tag_address[-1].split()[2:]).strip()
                            location_name = city
                        else:
                            street_address = " ".join(tag_address[:2]).strip()
                            city = tag_address[2].strip()
                            state = tag_address[3].strip()
                            zipp= tag_address[-1].strip()
                            location_name = city
                        # logger.info(street_address+" | "+city+" | "+state+" | "+zipp)
                        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')
                        phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(" ".join(list_details).split('Phone')[-1]))[0]
                        hours_of_operation = " ".join(list_details).split('Hours')[-1].strip()

                    else:
                        if "International Departure Level" in " ".join(list_details):
                            list_details.remove('International Departure Level, Post-security')
                        if "Calgary International Airport" in " ".join(list_details):
                            list_details.remove('Calgary International Airport')
                        # logger.info(list_details)
                        # logger.info(len(list_details))
                        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                        street_address =" ".join(list_details[0].split(',')[:-1]).strip()

                        if len(list_details[0].split(',')[-1].split()) !=2:

                            city = list_details[0].split(',')[-1].split()[0]
                            state = list_details[0].split(',')[-1].split()[1]
                            zipp = " ".join(list_details[0].split(',')[-1].split()[-2:]).strip()
                        else:
                            city = list_details[0].split(',')[-1].split()[0]
                            state = list_details[0].split(',')[-1].split()[1]
                            zipp = "<MISSING>"
                        phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(" ".join(list_details).split('Phone')[-1]))[0]
                        hours_of_operation = " ".join(list_details).split('Hours')[-1].strip()


                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                                 store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
                    store = ["<MISSING>" if x == ""  else x for x in store]
                    if ")" in store[8]:
                        if store[8][0] != "(":
                            store[8] = "(" + store[8]
                    # logger.info(location_name +" | "+street_address)

                    # logger.info("data = " + str(store))
                    # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    
                    for i in range(len(store)):
                        if type(store[i]) == str:
                            store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
                    store = [x.replace("–","-") if type(x) == str else x for x in store]
                    store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
                    return_main_object.append(store)


        except:
            # logger.info(loc_url)
            # logger.info('~~~~~~~~~~~~~~~~~~~~~')
            continue

    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
