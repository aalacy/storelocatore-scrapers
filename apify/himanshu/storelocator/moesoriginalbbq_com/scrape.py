import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    addresses = []
    base_url = "https://www.moesoriginalbbq.com/"
    r = session.get("https://api.storepoint.co/v1/159d567264b9aa/locations", headers=headers)
    # soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    locator_domain = base_url
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
    # page_url = ""
    json_data = r.json()
    # print('json_data ===== ' + str(len(json_data['results']['locations'])))
    for location_list in json_data['results']['locations']:
        location_name = location_list['name']
        store_number = str(location_list['id'])
        latitude = str(location_list['loc_lat'])
        longitude = str(location_list['loc_long'])
        phone = str(location_list['phone'])
        full_address = location_list['streetaddress'].replace("  ", " ")
        if not full_address.find('https://') >= 0:
            if len(full_address.split(',')[-1].strip().split(' ')) > 1:
                #print(full_address)
                street_address = ','.join(full_address.split(',')[:-2])
                city = full_address.split(',')[-2]
                if len(street_address) == 0:
                    street_address = full_address.split(',')[0]
                    city = '<MISSING>'
                state = full_address.split(',')[-1].strip().split(' ')[0]
                zipp = full_address.split(',')[-1].strip().split(' ')[1][-5:]
            else:
                street_address = ','.join(full_address.split(',')[:-3])
                city = full_address.split(',')[-3]
                if str(full_address.split(',')[-1])[-5:].isdigit():
                    zipp = full_address.split(',')[-1][-5:]
                    state = full_address.split(',')[-2]
                else:
                    zipp = full_address.split(',')[-2][-5:]
                    state = full_address.split(',')[-1]
                if "CDMX" in state:
                    continue
                # print(state,zipp)
        else:
            street_address = "<MISSING>"
            city = "<MISSING>"
            zipp = "<MISSING>"
            state = "<MISSING>"
        if "30381" == zipp:
            # 349 14th St.
            #print(zipp)
            zipp = "30318"
        # print("data === " + str(full_address))
        location_url = location_list['website']
        page_url = location_url.replace("/lo/rome","/rome")
        # print("location_url == "+ location_url)
        r_location = session.get(location_url, headers=headers)
        soup_location = BeautifulSoup(r_location.text, "lxml")
        if soup_location.find('h2') != None:
            hours = soup_location.find('h2')
            list_hours = list(hours.stripped_strings)
            list_hours = [el.replace('\xa0',' ') for el in list_hours]
            if "newark" in location_url or  "lo/granville" in location_url:
                hours_of_operation = "11am - 9pm MON-SAT"
            elif "rome" in location_url :
                hours_of_operation = "Sunday- Thursday: 11am - 9pm, Friday & Saturday: 11am - 10pm"
            elif "lo/breckenridge" in location_url:
                hours_of_operation = "<MISSING>"
            elif "moesdenver" in location_url and "Englewood" in city:
                tag_hours = soup_location.find('div',class_='hours').find_all('div',class_='hour')[-1].find('p')
                for br in tag_hours.find_all('br'):
                    br.replace_with(' ')
                hours_of_operation = tag_hours.text.strip()
                # print(hours_of_operation)
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~')
            elif "moesdenver" in location_url and "Denver" in city:
                tag_hours = soup_location.find('div',class_='hours').find_all('div',class_='hour')[0].find('p')
                for br in tag_hours.find_all('br'):
                    br.replace_with(' ')
                hours_of_operation = tag_hours.text.strip()
            elif "moesbbqcharlotte" in location_url and "Matthews" in city:
                # print(city)
                tag_hours= soup_location.find(lambda tag: (tag.name == 'h3') and "HOURS" in tag.text).find_next('p')
                for br in tag_hours.find_all('br'):
                    br.replace_with(' ')
                hours_of_operation = tag_hours.text.strip().split('Close')[0].strip()
                # print(city ,hours_of_operation)
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~')
            elif "moesbbqcharlotte" in location_url and "Waxhaw" in city:
                # print(city)
                tag_hours= soup_location.find_all(lambda tag: (tag.name == 'h3') and "HOURS" in tag.text)[-1].find_next('p')
                for br in tag_hours.find_all('br'):
                    br.replace_with(' ')
                hours_of_operation = tag_hours.text.strip().split('Close')[0].strip()
            else:
                hours_of_operation = " ".join(list_hours).strip().split('Address:')[0]
        else:
            hours = soup_location.find('div',{'id':'hours'})
            list_hours = list(hours.stripped_strings)
            list_hours = [el.replace('\xa0',' ') for el in list_hours]
        if "35603" in zipp:
            city = "Decatur"
            street_address = street_address.replace(" Decatur","")
        if "22902" in zipp:
            city = "Charlottesville"
            street_address = street_address.replace(" Charlottesville","")
        if "36575" in zipp:
            hours_of_operation = "Sun-Thu: 11am - 9pm, Fri - Sat: 11am - 10pm"
        if "temporarily" in hours_of_operation or "Temporarily" in hours_of_operation:
            hours_of_operation = "<MISSING>"
        if "Permanently Closed" in hours_of_operation or "Currently" in hours_of_operation or "We are currently doing " in hours_of_operation:
            hours_of_operation = "<MISSING>"
        store = [locator_domain, location_name, street_address.replace("120 Grove St.","700 NORTH LAKE BLVD").replace("6571 Highway 69 South","6571 Highway 69 South Suite A"), city.replace("Suite A Tuscaloosa","Tuscaloosa"), state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation.split(" 2101")[0].split("Curbside,")[0].replace("Hours of operation: ","").replace("Drive thru only","").replace("(Kitchen Closes @ 9pm) ","").replace("Open to in-house and patio dining. ","").replace("After a fire in the Smokehouse, we are serving from our Food Truck with limited menu.","").replace("Hours: Restaurant ",""),page_url]

        if country_code == "US" or country_code == "CA":
            if str(store[2]) + str(store[-3]) not in addresses:
                addresses.append(str(store[2]) + str(store[-3]))
                if "43023" in zipp:
                    continue
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
