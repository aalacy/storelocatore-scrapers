import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import sgzip
# import calendar

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
    # zips = sgzip.coords_for_radius(50)
    return_main_object = []
    addresses = []



    # headers = {
    #     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    #     "accept": "application/json, text/javascript, */*; q=0.01",
    #     # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    # }

    # it will used in store data.
    locator_domain = "https://extremepita.com/"
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

    url = "https://extremepita.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php"

    querystring = {"wpml_lang":"en","t":"1572423853390"}

    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache"
        # 'postman-token': "bfacba97-91fe-4384-39e2-993cf7f27740"
        }

    r = requests.request("GET", url, headers=headers, params=querystring)

    soup = BeautifulSoup(r.text,'lxml')
    for store in  soup.find('store').find_all('item'):

        location_name = store.find('location').text.replace('&amp;','and').replace('&#44;',",").replace('&#39;',"'")
        store_number = store.find('contactus').nextSibling.text.strip()
        address = store.find('address')
        list_address = list(address.stripped_strings)
        tag_address= " ".join(list_address).split(',')
        # print(tag_address)
        # print(len(tag_address))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        if len(tag_address) > 2:
            st_add = " ".join(tag_address[:-1]).split()
            street_address = " ".join(st_add[:-1]).replace('Red','').strip()
            if "Deer" != st_add[-1]:
                city =st_add[-1].strip()
            else:
                city = " ".join(st_add[-2:]).strip()
            state = tag_address[-1].split()[0].strip()
            zipp = " ".join(tag_address[-1].split()[-2:]).strip()

        else:
            zipp = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(tag_address[-1]))[0]
            # state =  " ".join(tag_address[-1].split())
            if len(tag_address[-1].split()) >2:
                state =  " ".join(tag_address[-1].split()[:-2])
            else:
                state = tag_address[-1].split()[0].strip()



            if len(tag_address[0].split('  ')) > 2:
                street_address = " ".join(tag_address[0].split('  ')[:-1]).strip()
                # print(street_address)
            else:
                street_address=tag_address[0].split('  ')[0]

            city = tag_address[0].split('  ')[-1].strip()
            tag_phone = store.find('telephone')
            list_phone = list(tag_phone.stripped_strings)
            if list_phone == []:
                phone  = "<MISSING>"
            else:
                phone= list_phone[0].split(';')[0]
            latitude = store.find('latitude').text.strip()
            longitude = store.find('longitude').text.strip()
            country_code = "CA"
            hours = store.find('exturl').nextSibling
            soup_hours = BeautifulSoup(hours.text,'lxml')
            # print(soup_hours.prettify())
            h = []
            for hr in soup_hours.find_all('p'):
                hour = hr.text.replace('\n' ,'  ')
                h.append(hour)
            hours_of_operation = "   ".join(h).replace('&','-').replace('\r','-').strip()
            page_url = "https://extremepita.com/locations/"



            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
            store = ["<MISSING>" if x == "" or x == "Blank" else x.encode('ascii', 'ignore').decode('ascii').strip() for x in store]
            # if store_number in addresses:
            #     continue
            # addresses.append(store_number)

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)
    #################################################
    #us store locator
    us_url = "https://locator.kahalamgmt.com/locator/index.php"
    # for zip_code in zips:
    us_querystring = {"brand":"27","mode":"map","latitude":"40.79843000","longitude":"-73.64766000","q":"","pagesize":""}

    us_headers = {
        'content-type': "application/x-www-form-urlencoded",
        'accept': "application/json, text/javascript, */*; q=0.01",
        'cache-control': "no-cache",
        'postman-token': "c5530775-1d0d-3c17-04e3-0cd229f54a0c"
        }

    us_response = requests.request("GET", us_url, headers=us_headers, params=us_querystring)
    us_soup = BeautifulSoup(us_response.text,'lxml')
    p_url = session.get('https://www.extremepitaus.com/locator/index.php?brand=27&mode=desktop&pagesize=5&q=11576')
    url_soup = BeautifulSoup(p_url.text,'lxml')
    u =[]
    h = []
    for loc_url in url_soup.find_all(lambda tag: (tag.name == 'a') and "Learn More" in tag.text):
        data_url = "https://www.extremepitaus.com"+loc_url['href']
        loc = session.get(data_url)
        soup_loc =BeautifulSoup(loc.text,'lxml')
        hours = soup_loc.find('div',class_='group hours').text.strip().replace('Store Hours','').strip()
        u.append(data_url)
        h.append(hours)

    script = us_soup.find('div',{'id':'map_canvas'}).find_next('script',{'type':'text/javascript'}).text.split('function()')[1].split(';')
    del script[-1]
    for i in script:

        script_text = i.split('=')[1].split('}')[0]+"}"
        try:
            json_data = json.loads(script_text)
        except:
            continue
        store_number = json_data['StoreId']
        location_name = json_data['Name']
        street_address = json_data['Address']
        city = json_data['City']
        state = json_data['State']
        zipp= json_data['Zip']
        phone = json_data['Phone']
        latitude = json_data['Latitude']
        longitude = json_data['Longitude']
        country_code = json_data['CountryCode']
        location_type = json_data['LocationType']
        hours_of_operation = h.pop(0)
        page_url = u.pop(0)

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
        store = ["<MISSING>" if x == "" or x == "Blank" else x for x in store]
        # if store_number in addresses:
        #     continue
        # addresses.append(store_number)

        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
