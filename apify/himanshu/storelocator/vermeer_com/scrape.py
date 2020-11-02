import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('vermeer_com')



session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # logger.info("data::" + str(data))
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
    base_url =  "https://www.vermeer.com"
    locator_domain = "https://www.vermeer.com"
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
    page_url = '<MISSING>'
    r = session.get('https://www.vermeer.com/NA/en/N/dealer_locator',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')





    for zip_code in zips:
        try:
            for select in soup.find('select',{'id':'SelectedIndustry'}).find_all('option')[1:]:
                val = select['value']



                url = "https://www.vermeer.com/NA/en/N/dealer_locator"

                querystring = {"SelectedIndustry":""+str(val)+"","LookupType":"ZipCode","Country":"US","ZipCode":""+str(zip_code)+""}
                # logger.info(querystring)
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')
                # logger.info(val,zip_code)

                payload = ""
                headers = {
                    'content-type': "application/x-www-form-urlencoded",
                    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                    'cache-control': "no-cache",
                    'postman-token': "b2637c4e-f26f-f3e0-6ce7-d01a9bb1d247"
                    }

                response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
                soup_loc = BeautifulSoup(response.text,'html.parser')
                address= soup_loc.find('div',{'class':'dealerContainer'})
                if address != None:
                    geo_list = soup_loc.find(lambda tag: (tag.name == 'script') and "function initMap" in tag.text).text.split('var data = [')[1].split('];')[0].strip().split('},')
                    geo =[]
                    for element in geo_list:
                        if element != '':
                            geo.append(element)
                    geo = [x.replace("\r\n","") for x in geo]
                    c1 = []
                    c2 = []
                    for coords in geo:
                        coord = coords+ "}".strip()
                        json_data = json.loads(coord)
                        lat = json_data['GeoLat']
                        lng= json_data['GeoLong']
                        c1.append(lat)
                        c2.append(lng)

                    for col in address.find_all('div',class_='col-lg-8'):
                        country_code = "US"
                        if "FOR" == str(val):
                            location_type = 'Agricultural'
                        if "IND" == str(val):
                            location_type = "Industrial"
                        list_col = list(col.stripped_strings)
                        location_name = list_col[0].strip()
                        # logger.info(location_type+" | "+street_address+ " | " +location_name)
                        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                        street_address = list_col[1].strip()
                        phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_col[4]))
                        if phone_list!=[]:
                            phone = phone_list[0].strip()
                        else:
                            phone = "<MISSING>"
                        latitude = c1.pop(0)
                        longitude = c2.pop(0)
                        csz = list_col[2].strip().split(',')
                        if len(csz) == 2:
                            city = csz[0].strip()
                            state = " ".join(csz[-1].split(' ')[:-1]).strip()
                            zipp = csz[-1].split(' ')[-1].strip()

                        else:
                            pass
                            # logger.info(csz)
                            # logger.info(len(csz))
                            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~`')
                else:
                    continue
                    # logger.info('https://www.vermeer.com/NA/en/N/dealer_locator?SelectedIndustry=IND&LookupType=ZipCode&Country=&ZipCode='+str(zip_code))
                    # logger.info('***********************************************')
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                store = [x if x else "<MISSING>" for x in store]

                if store[2] in addresses:
                    continue
                addresses.append(store[2])

                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                return_main_object.append(store)
        except:
            continue


   # logger.info('------------------------ CA locations -----------------------------------')

    #######   CA Locations   ############
    url = "https://www.vermeer.com/NA/en/N/dealer_locator"

    ca_querystring = {"SelectedIndustry":"IND","LookupType":"State","Country":"CA","State":"Alberta"}

    ca_payload = ""
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        'cache-control': "no-cache",
        'postman-token': "327e7310-91eb-55bc-dd59-8fd10e70bbc6"
        }

    ca_response = requests.request("POST", url, data=ca_payload, headers=headers, params=ca_querystring)

    ca_soup = BeautifulSoup(ca_response.text,'lxml')
    for state_loc in ca_soup.find('select',{'id':'State'}).find_all('option'):

        for select in ca_soup.find('select',{'id':'SelectedIndustry'}).find_all('option')[1:]:
            val = select['value']
            # logger.info(loc_type)
            if  "" != state_loc['value']:
                state = state_loc['value']
                ca_querystring = {"SelectedIndustry":""+str(val)+"","LookupType":"State","Country":"CA","State":""+str(state)+""}
                # logger.info(ca_querystring)
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')

                ca_payload = ""
                headers = {
                    'content-type': "application/x-www-form-urlencoded",
                    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                    'cache-control': "no-cache",
                    'postman-token': "327e7310-91eb-55bc-dd59-8fd10e70bbc6"
                    }

                ca_response = requests.request("POST", url, data=ca_payload, headers=headers, params=ca_querystring)

                ca_soup = BeautifulSoup(ca_response.text,'lxml')
                address= ca_soup.find('div',{'class':'dealerContainer'})
                if address != None:
                    geo_list = ca_soup.find(lambda tag: (tag.name == 'script') and "function initMap" in tag.text).text.split('var data = [')[1].split('];')[0].strip().split('},')
                    # logger.info(geo_list)
                    # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~')
                    geo =[]
                    for element in geo_list:
                        if element != '':
                            geo.append(element)
                    geo = [x.replace("\r\n","") for x in geo]
                    c1 = []
                    c2 = []
                    for coords in geo:
                        coord = coords+ "}".strip()
                        json_data = json.loads(coord)
                        lat = json_data['GeoLat']
                        lng= json_data['GeoLong']
                        c1.append(lat)
                        c2.append(lng)
                    # logger.info(c1,c2)
                    for col in address.find_all('div',class_='col-lg-8'):
                        country_code = "CA"
                        if "FOR" == str(val):
                            location_type = 'Agricultural'
                        if "IND" == str(val):
                            location_type = "Industrial"
                        list_col = list(col.stripped_strings)
                        location_name = list_col[0].strip()
                        street_address = list_col[1].strip()
                        # logger.info(location_type+" | "+street_address+ " | " +location_name)
                        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                        phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_col[4]))
                        if phone_list!=[]:
                            phone = phone_list[0].strip()
                        else:
                            phone = "<MISSING>"
                        latitude = c1.pop(0)
                        longitude = c2.pop(0)
                        csz = list_col[2].strip().split(',')
                        # logger.info(csz)
                        if len(csz) == 2:
                            city = csz[0].strip()
                            state = " ".join(csz[-1].split(' ')[:-2]).strip()
                            zipp =  " ".join(csz[-1].split(' ')[-2:]).strip()
                            if  "50219" in zipp:
                                # logger.info(ca_querystring)
                                continue
                            # logger.info(city+" | "+state+" | "+zipp)
                            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')

                        else:
                            pass
                            # logger.info(csz)
                            # logger.info(len(csz))
                            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~`')
                else:
                    continue
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                store = [x if x else "<MISSING>" for x in store]

                if store[2] in addresses:
                    continue
                addresses.append(store[2])

                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                return_main_object.append(store)

    return return_main_object



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
