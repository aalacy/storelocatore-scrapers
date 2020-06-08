import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import sgzip
session = SgRequests()
def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)
def fetch_data():
    # zips = sgzip.for_radius(50)
    return_main_object = []
    addresses = []
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    # it will used in store data.
    base_url = 'https://bluemartini.com/'
    locator_domain = "https://www.bluemartinilounge.com/"
    page_url = "<MISSING>"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = '<MISSING>'
    r = session.get(base_url,headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    for loc_slide in soup.find('ul',class_='loc-slide').find_all('li'):
        r_loc = session.get("https:"+loc_slide.a['href'],headers = headers)
        soup_loc = BeautifulSoup(r_loc.text,'lxml')
        nav = soup_loc.find('ul',{'id':'menu-mainnav-1'})
        if nav !=None:
            contact = nav.find(lambda tag: (tag.name == 'li') and "Contact" in tag.text)
            info_loc = session.get(contact.a['href'],headers = headers)
            info_soup = BeautifulSoup(info_loc.text,'lxml')
            page_url = contact.a['href']
            cont = info_soup.find('div',class_='cont-align-bottom')
            l_name = list(cont.h1.stripped_strings)
            location_name =" ".join(l_name[1:]).strip().capitalize()
            hours =  cont.find(lambda tag: (tag.name == 'p') and "Hours of Operation:" in tag.text)
            if hours != None:
                list_hours = list(hours.stripped_strings)
                hours_of_operation = " ".join(" ".join(list_hours).strip().split(':')[1:]).strip()
                # print(hours_of_operation)
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~`')
            else:
                hours = cont.find('p',class_='f25')
                list_hours = list(hours.stripped_strings)
                hours_of_operation = " ".join(" ".join(list_hours).strip().split(':')[1:]).strip()
            details = cont.find(lambda tag: (tag.name == 'p') and "Call:" in tag.text)
            if details !=None:
                list_details= list(details.stripped_strings)
                if len(list_details) >1:
                    phone = list_details[1].strip()
                else:
                    phone = "<MISSING>"
                address = list_details[-1].split(',')
                street_address = " ".join(address[:-2]).strip()
                city =address[-2].strip()
                state = address[-1].split()[0].strip()
                zipp = address[-1].split()[-1].strip()
                # print(street_address + " | "+city+ " | "+state+" | "+zipp)
            else:
                details = cont.find_all('p',class_='f30')[2]
                # print(details)
                if "Event Manager" not in details.text:
                    zipp = "34108"
                    list_details= list(details.stripped_strings)
                    street_address = "9114 Strada Place #12105"
                    city = "Naples"
                    state = "FL"
                    phone ="<MISSING>"
                else:
                    details = cont.find(lambda tag: (tag.name == 'p') and "Contact:" in tag.text)
                    list_details= list(details.stripped_strings)
                    street_address = list_details[-1].split(',')[0].strip()
                    city = list_details[-1].split(',')[-2].strip()
                    state = list_details[-1].split(',')[-1].split()[0].strip()
                    zipp = list_details[-1].split(',')[-1].split()[-1].strip()
                    phone = "<MISSING>"
        else:
            # comming soon location
            continue
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
             store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = [x if x else "<MISSING>" for x in store]

        if store[2] in addresses:
            continue
        addresses.append(store[2])
        #print("data = " + str(store))
        #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
