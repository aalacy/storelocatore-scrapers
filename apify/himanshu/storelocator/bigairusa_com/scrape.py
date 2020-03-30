import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json




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
    base_url = "https://www.bigairusa.com"
    locator_domain = "https://www.bigairusa.com"
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



    r= session.get('https://www.bigairusa.com',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    for link in soup.find('div',class_='textwidget').findAll('a'):
        loc_r= session.get(link['href'],headers = headers)
        soup_loc= BeautifulSoup(loc_r.text,'lxml')
        page_url = link['href'].strip()

        info = soup_loc.find('div',class_='fusion-row').find('div',class_ = 'fusion-contact-info')

        list_info = list(info.stripped_strings)
        address = list_info[0].split('|')
        if len(address) >1:
            location_name = address[0].split('•')[0].capitalize().strip()
            street_address = address[0].split('•')[-1].strip()
            city = address[1].split(',')[0].strip()
            state =address[1].split(',')[-1].strip()
            zipp = address[2].strip()
            phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(address[-1]))[0]
        else:
            add_tag = address[0].split('•')
            if len(add_tag) ==4:
                location_name = add_tag[0].strip()
                street_address = add_tag[-1].split(',')[0].strip()
                city = add_tag[-1].split(',')[1].strip()
                state = add_tag[-1].split(',')[-1].split()[0].strip()
                zipp = add_tag[-1].split(',')[-1].split()[-1].strip()
                phone = add_tag[2].strip()
            elif len(add_tag) ==3:
                phone =  re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), " ".join(add_tag))[0]
                zip = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(add_tag[-1]))
                if  zip != []:
                    location_name = add_tag[0].strip()
                    street_address = add_tag[-1].split(',')[0].strip()
                    city = add_tag[-1].split(',')[1].strip()
                    state = add_tag[-1].split(',')[-1].split()[0].strip()
                    zipp = zip[0].strip()
                    phone = add_tag[1].strip()
                else:

                    street_address = add_tag[0].strip()
                    city = add_tag[1].split(',')[0].strip()
                    state = add_tag[1].split(',')[-1].strip()
                    zipp = "<MISSING>"
                    phone = add_tag[-1].strip()
                    location_name = city
            else:
                add_tag = add_tag[0].split(',')
                if len(add_tag) ==4:
                    location_name = add_tag[0].strip()
                    phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(add_tag[1]))[0]
                    street_address =  " ".join(add_tag[1].split()[-4:]).strip()
                    city = add_tag[-2].strip()
                    state = add_tag[-1].split()[0].strip()
                    zipp= add_tag[-1].split()[-1].strip()

                else:
                    street_address = add_tag[0].strip()
                    city = add_tag[1].strip()
                    state = add_tag[-1].split()[0].strip()
                    zipp = add_tag[-1].split()[-1].strip()
                    location_name = city
                    if "greenville" in link['href']:
                        phone = soup_loc.find('footer').find('section',class_ = 'contact_info').find('p',class_ = 'phone').text.replace('Phone:','').strip()

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
        store = ["<MISSING>" if x == "" or x == None  else x for x in store]

        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)



    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
