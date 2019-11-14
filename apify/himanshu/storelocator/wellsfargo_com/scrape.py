import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)
def fetch_data():
    zips = sgzip.for_radius(50)
    return_main_object = []
    addresses = []

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',


    }

    # it will used in store data.
    base_url =  "https://www.wellsfargo.com/"
    locator_domain = "https://www.wellsfargo.com/"
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
    page_url = ''

    for zip_code in zips:
        # print(zip_code)
        # r = requests.get('https://www.wellsfargo.com/locator/search/?searchTxt=11576&mlflg=N&sgindex=99&chflg=N&_bo=on&_wl=on&_os=on&_bdu=on&_adu=on&_ah=on&_sdb=on&_aa=on&_nt=on&_fe=on')
        # print(r.text)

        try:
            r = requests.get('https://www.wellsfargo.com/locator/search/?searchTxt='+str(zip_code)+'&mlflg=N&sgindex=99&chflg=N&_bo=on&_wl=on&_os=on&_bdu=on&_adu=on&_ah=on&_sdb=on&_aa=on&_nt=on&_fe=on')

            soup =BeautifulSoup(r.text,'lxml')
            result = soup.find('div',{'id':'resultsSide'})
            # print(result.prettify())
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            for li in result.find_all('li',class_='aResult'):
                left_data = li.find('div',class_='vcard')
                adr = left_data.find('address',class_='adr')
                location_type = left_data.find('div',class_='fn heading').text.split('|')[0].strip().replace('+','and').strip()
                location_name = adr.find('div',{'itemprop':'addressLocality'}).text.strip().capitalize()
                street_address = adr.find('div',class_='street-address').text.strip().capitalize()
                city= adr.find('span',class_='locality').text.strip().capitalize()
                state = adr.find('abbr',class_='region').text.strip()
                zipp = adr.find('span',class_='postal-code').text.strip()
                #print(zipp)
                country_code = "US"
                phone_tag = left_data.find('div',class_='tel').text.replace('Phone:','').strip()
                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))
                if phone_list != []:
                    phone = phone_list[0].strip()
                else:
                    phone="<MISSING>"
                hours = li.find('div',class_='rightSideData')
                list_hours= list(hours.stripped_strings)
                if "Outage Alert" in list_hours:
                    list_hours.remove('Outage Alert')
                if "Unavailable:" in list_hours :
                    list_hours.remove('Unavailable:')
                if "ATMs" ==  list_hours[2]:
                    list_hours.remove('ATMs')
                    # print(list_hours)
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                if list_hours == []:
                    hours_of_operation = "<MISSING>"
                elif "Features" in list_hours[0]:
                    hours_of_operation = 'ATMs'+' '.join(list_hours).split('ATMs')[1].replace('&','and').strip()
                else:
                    hours_of_operation = " ".join(list_hours).strip().replace('&','and').strip()
                # print(hours_of_operation)
                # print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                page_url = 'https://www.wellsfargo.com/locator/search/?searchTxt='+str(zip_code)+'&mlflg=N&sgindex=99&chflg=N&_bo=on&_wl=on&_os=on&_bdu=on&_adu=on&_ah=on&_sdb=on&_aa=on&_nt=on&_fe=on'
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                store = [x if x else "<MISSING>" for x in store]

                if store[2] in addresses:
                    continue
                addresses.append(store[2])

                #print("data = " + str(store))
                #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                return_main_object.append(store)

        except:
            # print('https://www.wellsfargo.com/locator/search/?searchTxt='+str(zip_code)+'&mlflg=N&sgindex=99&chflg=N&_bo=on&_wl=on&_os=on&_bdu=on&_adu=on&_ah=on&_sdb=on&_aa=on&_nt=on&_fe=on')
            # print('****************************************************')
            continue






    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
