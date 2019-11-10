import csv
import requests
from bs4 import BeautifulSoup
import re
# import json
# import sgzip
# import calendar




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
    # zips = sgzip.coords_for_radius(50)
    return_main_object = []
    addresses = []



    # headers = {
    #     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    #     "accept": "application/json, text/javascript, */*; q=0.01",
    #     # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    # }

    # it will used in store data.
    locator_domain = "https://www.worldcasinodirectory.com/"
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



    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
        'Accept' :'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'}
    #CA location

    loc_type = requests.get('https://www.worldcasinodirectory.com/canada',headers = headers)
    soup_loc = BeautifulSoup(loc_type.text,'lxml')
    ul= soup_loc.find('ul',class_='statpanel')
    lt = []
    for li in ul.find_all('li'):
        data_url = "https:"+li.a['href']
        loc_type = li.a['href'].split('/')[-1]
        phone_tag = requests.get(data_url,headers = headers)
        soup_phone = BeautifulSoup(phone_tag.text,'lxml')
        ph = soup_phone.find('table').find('tbody')
        p = []
        for tr in ph.find_all('tr'):
            # print(tr.text)
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(tr.text))
            if phone_list == []:
                phone = "<MISSING>"
            else:
                phone =phone_list[0].strip()
            p.append(phone)

        if "casino-list" == loc_type:

            r = requests.get('https://www.worldcasinodirectory.com/canada/map',headers = headers)
            soup= BeautifulSoup(r.text,'lxml')
            # col = soup.find('div',class_='col-md-9')
            # section =col.find_all('div',class_='section-white')[-1]

            for loc in soup.find_all('div',class_='map-destination-link'):
                country_code = "CA"
                location_name = loc.find('h3',class_='map-data-name').text.strip()
                address = loc.find('span',class_='map-data-address')
                list_address = list(address.stripped_strings)

                spilt_address=  " ".join(list_address).split(',')
                zipp_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(spilt_address[-2]))
                if zipp_list == []:
                    zipp = "<MISSING>"
                else:
                    zipp= zipp_list[0].strip()
                state = spilt_address[-2].split()[0]
                # print(spilt_address)
                # print(len(spilt_address))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                if len(spilt_address) == 5:
                    city = spilt_address[2].strip()
                    street_address = " ".join(spilt_address[:2]).strip()
                elif len(spilt_address) == 4:

                    city = spilt_address[1].strip().replace('S7K 2L2','')
                    street_address = spilt_address[0].strip()
                    # print(city)
                else:
                    city = spilt_address[1].strip()
                    street_address = "<MISSING>"
                    # print(loc.prettify())
                latitude = loc.find('span',class_='map-data-latitude').text.strip()
                longitude = loc.find('span',class_='map-data-longitude').text.strip()
                location_type = loc_type.split('-')[0].strip()
                phone = p.pop(0).replace('(','').replace(')','').strip()
                page_url = "https://www.worldcasinodirectory.com/casino/"+loc.find('span',class_='map-data-title').text.strip()

                hours = requests.get(page_url,headers = headers)
                soup_hours = BeautifulSoup(hours.text,'lxml')
                hr = soup_hours.find('div',class_='12u marginT20')
                if hr != None:
                    hr_table = hr.find('table')
                    if hr_table != None:
                        hours_of_operation = hr_table.text.replace('\n',' ')
                        # print(hours_of_operation)
                        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    else:
                        hours_of_operation = "<MISSING>"
                else:
                    hours_of_operation = "<MISSING>"
                    # print(page_url)
                    # print('*****************************************')
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
                store = ["<MISSING>" if x == ""  or x== None else x for x in store]
                if street_address in addresses:
                    continue
                addresses.append(street_address)

               # print("data = " + str(store))
               # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                return_main_object.append(store)
        else:
            pass




    #us location
    us_loc_type = requests.get('https://www.worldcasinodirectory.com/united-states',headers = headers)
    us_soup_loc = BeautifulSoup(us_loc_type.text,'lxml')
    us_ul= us_soup_loc.find('ul',class_='statpanel')
    us_lt = []
    for li in us_ul.find_all('li'):
        data_url = "https:"+li.a['href']
        # print(data_url)
        loc_type = li.a['href'].split('/')[-1]
        if "casino-list" == loc_type:
            phone_tag = requests.get(data_url,headers = headers)
            soup_phone = BeautifulSoup(phone_tag.text,'lxml')
            ph = soup_phone.find('table').find('tbody')
            p = []
            for tr in ph.find_all('tr'):
                # print(tr.text)
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(tr.text))
                if phone_list == []:
                    phone = "<MISSING>"
                else:
                    phone =phone_list[0].strip()
                p.append(phone)






            us_r = requests.get('https://www.worldcasinodirectory.com/united-states/map',headers = headers)
            soup_us = BeautifulSoup(us_r.text,'lxml')
            for loc in soup_us.find_all('div',class_='map-destination-link'):
                country_code = "US"
                location_name = loc.find('h3',class_='map-data-name').text.strip().replace('&','and').strip()
                # print(location_name)
                address = loc.find('span',class_='map-data-address')
                list_address = list(address.stripped_strings)

                if list_address !=[]:
                    spilt_address=  " ".join(list_address).split(',')
                    zipp_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(spilt_address[-2]))
                    if zipp_list == []:
                        zipp= "<MISSING>"
                    else:
                        zipp = zipp_list[0].strip()

                    state = spilt_address[-2].split()[0]
                    # print(spilt_address)
                    # print(len(spilt_address))
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    if len(spilt_address) == 5:
                        city = spilt_address[2].strip()
                        street_address = " ".join(spilt_address[:2]).strip()
                    elif len(spilt_address) == 4:

                        city = spilt_address[1].strip().replace('S7K 2L2','')
                        street_address = spilt_address[0].strip()
                        # print(city)
                    elif len(spilt_address) == 3:
                        city = spilt_address[1].strip()
                        street_address = "<MISSING>"
                        # print(loc.prettify())
                    elif len(spilt_address) == 2 and "U.S. 81" not in spilt_address[0]:
                        city = spilt_address[0].strip()
                        street_address = "<MISSING>"
                    elif len(spilt_address) == 2 and "U.S. 81" in spilt_address[0]:
                        street_address = spilt_address[0]
                        city = "<MISSING>"
                    else:
                        street_address = " ".join(spilt_address[:3]).strip()
                        city = spilt_address[3].strip()
                else:
                    # print(loc.prettify())
                    street_address = "<MISSING>"
                    city = "<MISSING>"
                    state = "<MISSING>"
                    zipp= "<MISSING>"

                    latitude = loc.find('span',class_='map-data-latitude').text.strip()
                    longitude = loc.find('span',class_='map-data-longitude').text.strip()
                    location_type = loc_type.split('-')[0].strip()
                    phone = p.pop(0).replace('(','').replace(')','').strip()
                    page_url = "https://www.worldcasinodirectory.com/casino/"+loc.find('span',class_='map-data-title').text.strip()
                    hours = requests.get(page_url,headers = headers)
                    soup_hours = BeautifulSoup(hours.text,'lxml')
                    hr = soup_hours.find('div',class_='12u marginT20')
                    if hr != None:
                        hr_table = hr.find('table')
                        if hr_table != None:
                            hours_of_operation = hr_table.text.replace('\n',' ')
                            # print(hours_of_operation)
                            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                        else:
                            hours_of_operation = "<MISSING>"
                    else:
                        hours_of_operation = "<MISSING>"
                        # print(page_url)
                        # print('*****************************************')

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
                store = ["<MISSING>" if x == ""  or x== None else x for x in store]
                if street_address in addresses:
                    continue
                addresses.append(street_address)

                #print("data = " + str(store))
                #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                return_main_object.append(store)
        else:
            pass


    return return_main_object



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
