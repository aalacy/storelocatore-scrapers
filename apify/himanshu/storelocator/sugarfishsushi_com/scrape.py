import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
# import json
# import sgzip
# import time



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
    locator_domain = "https://sugarfishsushi.com/"
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
    page_url = "<MISSING>"



    r= session.get('https://sugarfishsushi.com/our-locations/',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    a= soup.find('div',class_="container")
    for x in a.find_all('strong'):
        # page_url = x.a['href']
        if x.a is not None:
            page_url = x.a['href']
            r_loc = session.get(x.a['href'],headers = headers)
            soup_loc = BeautifulSoup(r_loc.text,'lxml')
            info = soup_loc.find('div',class_='entry-content').h6
            # print(info.prettify())

            list_info = list(info.stripped_strings)
            list_info = [el.replace('\xa0',' ') for el in list_info]
            if len(list_info) ==4:
                location_name = list_info[0]
                street_address = list_info[1]
                city = list_info[2].split(',')[0]
                state = list_info[2].split(',')[1].split()[0]
                zipp = list_info[2].split(',')[1].split()[-1]
                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_info[-1]))
                phone= phone_list[0]
            elif len(list_info) == 5:
                location_name = list_info[0]
                street_address = " ".join(list_info[1:3])
                city = list_info[3].split(',')[0]
                state = list_info[3].split(',')[1].split()[0]
                zipp = list_info[3].split(',')[1].split()[-1]
                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_info[-1]))
                phone= phone_list[0]
            elif list_info ==[]:

                info = soup_loc.find('div',class_='entry-content').find('div',class_='column4').h6
                list_info = list(info.stripped_strings)

                location_name =list_info[0]
                street_address = list_info[1]
                city = list_info[2].split(',')[0]
                state = list_info[2].split(',')[1].split()[0]
                zipp = list_info[2].split(',')[1].split()[-1]
                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_info[-1]))
                phone= phone_list[0]

            else:

                info = soup_loc.find('div',class_='entry-content').find('div',class_='column4').find_all('h6')[2]
                list_info = list(info.stripped_strings)
                location_name =list_info[0]
                street_address = list_info[1]
                city = list_info[2].split(',')[0]
                state = list_info[2].split(',')[1].split()[0]
                zipp = list_info[2].split(',')[1].split()[-1]
                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_info[-1]))
                phone= phone_list[0]

            hours = info = soup_loc.find('div',class_='entry-content').find_all('h6')[1]
            list_hours = list(hours.stripped_strings)
            list_hours = [el.replace('\xa0',' ') for el in list_hours]
            if list_hours !=[]:
                if "Monday through " in list_hours[0] :
                    if len(list_hours) ==4 or len(list_hours) == 6:
                        hours_of_operation = " ".join(list_hours)

                    else:

                        hours_of_operation = " ".join(list_hours[:4])
                else:
                    hours = info = soup_loc.find('div',class_='entry-content').find('div',class_ = 'column4').find_all('h6')[1]
                    list_hours = list(hours.stripped_strings)
                    hours_of_operation = " ".join(list_hours)
            else:
                hours = soup_loc.find('div',class_='entry-content').find('div',class_='column4').find_all('h6')[3]
                list_hours = list(hours.stripped_strings)
                hours_of_operation = " ".join(list_hours)







            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
            store = ["<MISSING>" if x == "" else x for x in store]

            # print("data = " + str(store))
            # print(
            #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)

    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
