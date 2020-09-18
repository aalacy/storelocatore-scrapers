import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url = "http://topsbarbq.com/"
    locator_domain = "http://topsbarbq.com/locations/"
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
    page_url = locator_domain
    r = session.get('http://topsbarbq.com/locations', headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    # for section in soup.find_all('section',class_='loc-row'):
    for loc_col in soup.find_all('div', {'class': 'loc-col'}):
        location_name = loc_col.h3.text.strip()
        address = loc_col.find('p', class_='elementor-heading-title')
        latitude = address.find('a')['href'].split(
            '@')[-1].split(',')[0].strip()
        longitude = address.find('a')['href'].split(
            '@')[-1].split(',')[1].strip()
        list_address = list(address.stripped_strings)
        street_address = list_address[0].strip()
        city = list_address[-1].split(',')[0].replace("38107","").strip()
        state = list_address[-1].split(',')[-1].split()[0].strip()
        if "Memphis" in state:
            state = "TN"
        zipp = list_address[-1].split(',')[-1].split()[-1].strip()
        hours_of_operation = loc_col.find(
            'div', class_='loc-hours').text.strip().replace('\n', "   ").replace('Hours:', '').strip()
        if "Drive" in hours_of_operation:
            hours_of_operation = hours_of_operation[:hours_of_operation.find("Drive")].strip()
        hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()
        phone = loc_col.find_all(
            'div', class_='elementor-widget-container')[-1].text.strip()
        store = []
        store.append(base_url if base_url else "<MISSING>")
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append(store_number if store_number else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append(location_type if location_type else "<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(
            hours_of_operation if hours_of_operation else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")
        return_main_object.append(store)
        # print(str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    return return_main_object

    # store_name=[]
    # store_detail=[]
    # return_main_object=[]
    # phone = []
    # k = soup.find_all("div",{"class":"entry-content"})
    # for target_list in k:
    #     p =target_list.find_all("div",{"class":"et_pb_text_inner"})
    #     for p1 in p:
    #         tem_var =[]
    #         if len(list(p1.stripped_strings))==7:
    #             store_name.append(list(p1.stripped_strings)[0])
    #             street_address = list(p1.stripped_strings)[2].split(',')[0]
    #             print(street_address)
    #             city = list(p1.stripped_strings)[2].split(',')[1]
    #             state=list(p1.stripped_strings)[2].split(',')[2].split( )[0]
    #             zipcode = list(p1.stripped_strings)[2].split(',')[2].split( )[1]

    #             phone = (list(p1.stripped_strings)[6])

    #             hours =  (list(p1.stripped_strings)[4])

    #             tem_var.append(street_address)
    #             tem_var.append(city)
    #             tem_var.append(state.strip())
    #             tem_var.append(zipcode.strip())
    #             tem_var.append("US")
    #             tem_var.append("<MISSING>")
    #             tem_var.append(phone)
    #             tem_var.append("topsbarbq")
    #             tem_var.append("<MISSING>")
    #             tem_var.append("<MISSING>")
    #             tem_var.append(hours)
    #             store_detail.append(tem_var)

    # for i in range(len(store_name)):
    #     store = list()
    #     store.append("http://topsbarbq.com")
    #     store.append(store_name[i])
    #     store.extend(store_detail[i])
    #     print("data == "+str(store))
    #     print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    #     return_main_object.append(store)

    # return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
