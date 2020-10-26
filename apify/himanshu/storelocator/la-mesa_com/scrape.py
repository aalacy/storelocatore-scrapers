import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
# import json
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
    base_url = 'https://la-mesa.com/'
    locator_domain = "https://la-mesa.com/"
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
    page_url = ''

    coords = session.get('https://la-mesa.com/locations/',headers=headers)
    c_soup = BeautifulSoup(coords.text,'lxml')
    c1 = []
    c2 = []
    for coord in c_soup.find_all('div',class_='et_pb_code_inner'):
        co = coord.find("iframe")['src'].split("2d")[1].split("!1")[0].replace("!2m3","").replace("!3m2","").split("!3d")
        c1.append(co[1])
        c2.append(co[0])



    r = session.get('https://la-mesa.com/',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    ul= soup.find('ul',{'id':'top-menu'})
    li = soup.find(lambda tag: (tag.name == "li") and "Locations" in tag.text).find('ul',class_='sub-menu')
    for a in li.find_all('a'):
        page_url = a['href']
       
        r_loc = session.get(a['href'],headers = headers)
        soup_loc = BeautifulSoup(r_loc.text,'lxml')
        address= soup_loc.find('div',class_='et_pb_blurb_description')
        list_address= list(address.stripped_strings)
        location_name =list_address[0].strip()
        street_address = list_address[1].strip()
        city = list_address[2].split(',')[0].strip()
        state = list_address[2].split(',')[-1].split()[0].strip()
        zipp = list_address[2].split(',')[-1].split()[-1].strip()
        phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(" ".join(list_address[3:])))[0].strip()
        link_list = ["https://la-mesa.com/locations/papillion/829-tara-plz/","https://la-mesa.com/locations/bellevue/1405-fort-crook-rd-s/"]
        if page_url in link_list:
            hours = soup_loc.find_all("div",{"class":"et_pb_text_inner"})[4]
            list_hours = list(hours.stripped_strings)
            hours_of_operation = "  ".join(list_hours).strip()
        else:

            try:
                hours = soup_loc.find("div",{"class":"et_pb_row et_pb_row_2"}).find("div",{"class":"et_pb_text_inner"})
                list_hours = list(hours.stripped_strings)
                hours_of_operation = "  ".join(list_hours).strip()
            except:
                hours = soup_loc.find("div",{"class":"et_pb_row et_pb_row_0"}).find("div",{"class":"et_pb_text_inner"})
                list_hours = list(hours.stripped_strings)
                hours_of_operation = "  ".join(list_hours).strip()

        latitude = c1.pop(0)
        longitude = c2.pop(0)

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
             store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = [x if x else "<MISSING>" for x in store]
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]

        if store[2] in addresses:
            continue
        addresses.append(store[2])
        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
