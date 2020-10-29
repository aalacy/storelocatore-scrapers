import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import sgzip
import json
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('homestarbank_com')


s = requests.Session()


session = SgRequests()

def write_output(data1, data2):
    with open('data.csv',newline="", mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data1:
            writer.writerow(row)
        for row in data2:
            writer.writerow(row)

##### ATMS  #########

def fetch_data2():
    base_url = "https://www.midlandsb.com/homestar-and-midland"
    return_main_object = []
    addresses2 = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 80
    coords = search.next_coord()
    header = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
              "Content-Type": "application/x-www-form-urlencoded"
              # "Referer": "https://bylinebank.locatorsearch.com/index.aspx?s=FCS"
              }
    while coords:
        result_coords = []
        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        try:
            url = 'https://midlandsb.locatorsearch.com/GetItems.aspx'
            data = "lat=" + str(coords[0]) + "&lng=" + str(coords[1]) + \
                "&searchby=FIATM%7C&SearchKey=&rnd=1589454899459"
            # logger.info(coords)
            s = requests.Session()
            r = session.post(
                'https://midlandsb.locatorsearch.com/GetItems.aspx',
                headers=header, data=data,
            )
        except:
            continue
        addresses = []
        try:
            pagereq = s.get(url, data=data, headers=header)
        except:
            continue
        soup = BeautifulSoup(pagereq.content, 'html.parser')
        loc = soup.find_all('marker')
        for x in soup.find_all('marker'):
            latitude = x['lat']
            longitude = x['lng']
            location_type = "ATM"
            loc_name = x.find('title').text.strip().replace('<br>', '')
            if "</a>" in loc_name:
                location_name = loc_name.split(
                    '>')[1].replace('</a', '').strip().replace('<br>', '')
                # lname = BeautifulSoup(location_name, 'lxml')
                # location_name = lname.find('a').text.strip()
            else:
                location_name = loc_name.replace('<br>', '')

            street_address = x.find('add1').text.strip()
            city = x.find('add2').text.split(',')[0].strip()
            string = x.find('add2').text
            phone_list = re.findall(re.compile(
                ".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(string))
            ca_zip_list = re.findall(
                r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(string))
            us_zip_list = re.findall(re.compile(
                r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(string))
            state_list = re.findall(r' ([A-Z]{2}) ', str(string))
            if state_list:
                state = state_list[-1].strip()
            else:
                state = "<MISSING>"
            if phone_list:
                phone = phone_list[-1].strip()
            else:
                phone = "<MISSING>"
            if us_zip_list:
                zipp = us_zip_list[-1].strip()
                country_code = "US"
            elif ca_zip_list:
                zipp = ca_zip_list[-1].strip()
                country_code = "CA"
            else:
                continue
            # logger.info(zipp)
            hours_of_operation = "<MISSING>"
            store_number = "<MISSING>"
            locator_domain = "https://homestarbank.com"

            result_coords.append((latitude, longitude))
            # if street_address in addresses2:
            #     continue
            # addresses2.append(street_address)
            store = []
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zipp if zipp else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append(location_type if location_type else '<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(
                hours_of_operation if hours_of_operation else '<MISSING>')
            store.append("https://www.midlandsb.com/location")
            # attr = store[1] + "" + store[2] + "" + \
            #     store[3] + "" + store[4] + "" + store[5]

            if (store[1]+" "+store[2]) in addresses2:
                continue 
            addresses2.append(store[1]+" "+store[2])
            yield store
            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        if len(loc) < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(loc) == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " +
                            str(MAX_RESULTS) + " results")
        coords = search.next_coord()

#####  branches  ######


def fetch_data1():
    base_url = "https://www.midlandsb.com/homestar-and-midland"
    # conn = http.client.HTTPSConnection("guess.radius8.com")
    return_main_object = []
    addresses1 = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 80
    coords = search.next_coord()
    header = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
              "Content-Type": "application/x-www-form-urlencoded"
              # "Referer": "https://bylinebank.locatorsearch.com/index.aspx?s=FCS"
              }
    while coords:
        # try:
        result_coords = []
        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # logger.info(coords[0], coords[1])

        try:
            url = 'https://midlandsb.locatorsearch.com/GetItems.aspx'
            data = "lat=" + str(coords[0]) + "&lng=" + str(coords[1]) + \
                "&searchby=FCS%7C&SearchKey=&rnd=1589454899459"
            # logger.info(coords)
            
            r = session.post(
                'https://midlandsb.locatorsearch.com/GetItems.aspx',
                headers=header, data=data,
            )
        except Exception as e:
            continue
            # pass
            # logger.info(e)
        addresses = []
        country_code = "US"
        try:
            pagereq = s.get(url, data=data, headers=header)
        except Exception as e:
            continue
            # pass
            # logger.info(e)
        soup = BeautifulSoup(pagereq.content, 'html.parser')
        add2 = soup.find_all("add2")
        address1 = soup.find_all("add1")
        loc = soup.find_all("marker")
        # lat1 = loc[1].attrs['lat']
        # lng1 = loc[1].attrs['lng']
        # logger.info(soup)
        hours = soup.find_all("contents")
        name = soup.find_all("title")
        locator_domain = "https://homestarbank.com"
        store_number = "<MISSING>"

        for i in range(len(address1)):
            street_address = address1[i].text
            city = add2[i].text.replace("<br>", ",").replace(
                "<b>", "").replace("</b>", "").strip().split(",")[0]
            state = add2[i].text.replace("<br>", ",").replace(
                "<b>", "").replace("</b>", "").strip().split(",")[1].split()[0]
            zip1 = add2[i].text.replace("<br>", ",").replace(
                "<b>", "").replace("</b>", "").strip().split(",")[1].split()[1]
            phone1 = add2[i].text.replace("<br>", ",").replace(
                "<b>", "").replace("</b>", "").strip()

            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone1))
            if phone_list:
                phone =  phone_list[-1]
            if len(name[i].text.split(">")) > 1:
                location_name = name[i].text.split(">")[1].replace("</a", "")
            else:
                location_name = name[i].text
                # logger.info(location_name)
            if "Monday:" in hours[i].text:
                soup_hour = BeautifulSoup(hours[i].text, 'lxml')
                h = []
                for tr in soup_hour.find('table').find_all('tr'):
                    list_tr = list(tr.stripped_strings)
                    if len(list_tr) == 1:
                        hour = "<MISSING>"

                    else:
                        hour = " ".join(list_tr)
                    h.append(hour)
                if "<MISSING>" in " ".join(h):
                    hours_of_operation = "<MISSING>"

                else:
                    hours_of_operation = "  ".join(h)
                location_type = 'branch'
                # logger.info(hours_of_operation)
                # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

                # hours_of_operation = (hours[i].text.replace("</td><td>", " ").replace("<tr><td>","").replace("</td></tr>"," ").replace("</table><div>"," ").replace("<br>"," ").replace(" </div>","").split("'0'>")[1].replace("</div>",""))
            # logger.info(hours1)
            # logger.info(add2[i].text.replace("<br>",",").replace("<b>","").replace("</b>","").strip().split(",")[2])

            latitude = loc[i].attrs['lat']
            longitude = loc[i].attrs['lng']
            result_coords.append((latitude, longitude))
            store = []
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zip1 if zip1 else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append(location_type if location_type else '<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(
                hours_of_operation if hours_of_operation else '<MISSING>')
            store.append("https://www.midlandsb.com/location")
            # attr = store[1] + "" + store[2] + "" + \
            #     store[3] + "" + store[4] + "" + store[5]
            if (store[1]+" "+store[2]) in addresses1:
                continue 
            addresses1.append(store[1]+" "+store[2])

            yield store
            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        if len(loc) < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(loc) == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " +
                            str(MAX_RESULTS) + " results")
        coords = search.next_coord()





def scrape():
    data1 = fetch_data1()
    data2 = fetch_data2()
    write_output(data1, data2)


scrape()
