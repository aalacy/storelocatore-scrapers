import csv
import requests
from bs4 import BeautifulSoup
import re

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
    locator_domain = "https://www.scoregolf.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "CA"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    url = "https://scoregolf.com/golf-course-guide/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
        'Accept' :'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'}

    r = requests.request("GET", url, headers=headers)
    soup = BeautifulSoup(r.text,'lxml')
    for li in soup.find('div',class_='crs-province').find('ul',class_='crs-by-prov').find_all('li',class_='crs-province-list'):
        for h5  in  li.find_all(lambda tag: (tag.name == "h5" and "Cities in " not in tag.text)):
            a = "https://www.scoregolf.com"+h5.find('a')['href']
            r_loc = requests.get(a,headers = headers)
            soup_loc = BeautifulSoup(r_loc.text,'lxml')

            try:
                table = soup_loc.find('table',class_='tablesorter')
                tbody = table.find('tbody')
                for loc_url in tbody.find_all('a'):
                    page_url = "https://www.scoregolf.com"+loc_url['href']
                    rr = requests.get(page_url,headers = headers)
                    soup_rr = BeautifulSoup(rr.text,'lxml')
                    block = soup_rr.find('div',class_='block cg-wrapper').find('div',class_='facility-info-wrapper').find_all('div',class_ = 'large-4 medium-4 small-12 columns')[-1]
                    address= block.find('div',class_='cg-address')
                    list_address= list(address.stripped_strings)
                
                    st_address = list_address[1].replace('\\u200b','').strip()
                    if ","  == st_address:
                        street_address = "<MISSING>"
                    else:
                        street_address = st_address
                    city = list_address[-2].split(',')[0].strip()
                    state_tag = list_address[-2].split(',')[-1].strip()
                    if "Yukon and Territories" == state_tag:
                        state = "<MISSING>"
                    else:
                        state = state_tag
                    ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(list_address[-1]))
                    if ca_zip_list == []:
                        zipp= "<MISSING>"
                    else:
                        zipp= ca_zip_list[0].strip()
               
                    # print(zipp +" | "+state)
                    lname = soup_rr.find('div',class_='block cg-wrapper').find('div',class_= 'block crs-header-block')
                    location_name = list(lname.stripped_strings)[0].capitalize().strip()
                    phone_tag=soup_rr.find('div',class_='block cg-wrapper').find('div',class_='facility-info-wrapper').find('p',class_ = 'exp-tx').text.strip()
                    phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))
                    if phone_list != []:
                        phone = phone_list[0].strip()
                    else:
                        phone = "<MISSING>"
                    lat = soup_rr.find('div',class_ = 'blockbox wrap-4 mapresult').find_next('script',{'type':'text/javascript'}).text.split('initFacMap(')[1].split(',')[0].split('.')[0]
                    lng = soup_rr.find('div',class_ = 'blockbox wrap-4 mapresult').find_next('script',{'type':'text/javascript'}).text.split('initFacMap(')[1].split(',')[1].split('.')[0]
                    if  "0" == lat :
                        latitude = "<MISSING>"
                    else:
                        latitude = soup_rr.find('div',class_ = 'blockbox wrap-4 mapresult').find_next('script',{'type':'text/javascript'}).text.split('initFacMap(')[1].split(',')[0]
                    if "0" == lng :
                        longitude= "<MISSING>"
                    else:
                        longitude = soup_rr.find('div',class_ = 'blockbox wrap-4 mapresult').find_next('script',{'type':'text/javascript'}).text.split('initFacMap(')[1].split(',')[1]
             
                    store = [locator_domain, location_name.capitalize(), street_address.capitalize().replace(","," ").replace(".,","").replace(". ,","").replace("#",""), city.capitalize(), state, zipp, country_code,
                         store_number, phone.replace(")",""), location_type, latitude, longitude.replace("0.0000000000","<MISSING>"), hours_of_operation,page_url]
                    store = ["<MISSING>" if x == "" or x == ","  or x == None else x.encode('ascii', 'ignore').decode('ascii').strip() for x in store]
                    if store[2] in addresses:
                        continue
                    addresses.append(store[2])
                    store[2] = " ".join(list(BeautifulSoup(store[2],"lxml").stripped_strings))
                    # print("data = " + str(store))
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    if store[2] == "":
                        store[2] = "<MISSING>"
                    if store[2] == None:
                        store[2] = "<MISSING>"
                    if store[-4] == "<MISSING>":
                        store[-3] = "<MISSING>"
                    if store[-3] == "<MISSING>":
                        store[-4] = "<MISSING>"
                    yield store
                    # return_main_object.append(store)


            except:
                continue
                





    # return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
