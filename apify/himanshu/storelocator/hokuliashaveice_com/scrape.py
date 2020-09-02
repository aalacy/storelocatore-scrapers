import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import sgzip
# import time
import html5lib



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
    locator_domain = "https://hokuliashaveice.com"
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



    r= session.get('https://hokuliashaveice.com/locations/',headers = headers)
    soup = BeautifulSoup(r.text,'html5lib')
    script= soup.find('div',{'id':'locations'}).find_next('script')
    s = script.text.split(' var features = ')[-1].split('];')[0] + ']'.replace('\n','')
    sc= s.split(' position:')
    sc.pop(0)
    # print(sc)
    for i in sc:
        info = i.replace('\n','').replace('  ','')
        latitude= info.split('(')[1].split(')')[0].split(',')[0]
        longitude = info.split('(')[1].split(')')[0].split(',')[-1]
        address = info.split('message:')[-1].split('<br>')[0].replace('"','').split('<br />')
        # address = [el.replace('',' ') for el in address]
        add_list = []
        for element in address:
            if element != '':
                add_list.append(element)

        # print (add_list)
        # print(address)
        # print(len(address))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~')
        if len(add_list) ==2:
            # print(address)
            # print(len(address))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~')
            add= " ".join(add_list).split(',')

            if len(add) == 2:
                street_address = add[0]
                if len(add[-1].split()) ==1:
                    city = add[0].split()[-1]
                    state = add[-1]
                    zipp = "<MISSING>"
                    location_name = city
                else:
                    # print(add[-1].split())
                    city = add[-1].split()[0]
                    state = add[-1].split()[1]
                    zipp = add[-1].split()[-1]
                    location_name = city
                # print(street_address,city,state,zipp)
            else :
                # print(add)
                # print(len(add))
                # print('~~~~~~~~~~~~~~`')
                street_address =add[0].strip()
                city = add[-2].strip()
                state = add[-1].split()[0]
                zipp = add[-1].split()[-1]
                # print(zipp,state)
        elif len(add_list) ==3:
            # print(add_list)
            # print(len(add_list))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~')
            if " 1143 Prince Ave" not in add_list[0] and " 3341 Lexington Road" not in add_list[0]:
                location_name = add_list[0].strip()
                street_address = add_list[1]
                city = add_list[2].split(',')[0]

                sz= add_list[2].split(',')[-1]
                # print(sz.split())
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(sz))
                if us_zip_list != []:
                    zipp = us_zip_list[0]
                    # print(zipp)
                else:
                    m = re.findall(r'\d', sz)
                    zip = "".join(m)
                    # print(zip.split())
                    if zip.split() != []:
                        zipp= zip
                        # print(zipp)
                    else :
                        zipp = "<MISSING>"

                if len(sz.split()) ==2:
                    state = sz.split()[0].strip()
                    # print(state)
                else:
                    # a = re.findall(r'^\w+$',sz)
                    if zip.split() != []:
                        state = sz.split(zip)[0].strip()
                        # print(state)
                    else:
                        state = sz.strip()
                # print(state,zipp)
                # print(street_address +"|"+city+"|"+state+"|"+zipp +"|"+location_name)
                # print(state)
            else:
                # print(add_list)
                # print(len(add_list))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~')
                street_address = add_list[0].strip()
                city="Athens"
                state = "GA"
                zipp_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), " ".join(add_list))
                if zipp_list == []:
                    zipp  = "<MISSING>"
                else:
                    zipp = zipp_list[0]
                location_name = city
                # print(street_address +"|"+city+"|"+state+"|"+zipp +"|"+location_name)
        elif len(add_list) == 4:
            # print(add_list)
            # # # # print(len(address))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~')
            location_name = add_list[0].strip()
            street_address = " ".join(add_list[1:-1]).replace(', KS 66061','')
            # print(street_address)
            csz = add_list[-1].split(',')
            if len(csz) >1:
                city = csz[0].strip()
                if len(csz[1].split()) ==1:
                    state = csz[1].split()[0]
                    zipp = "<MISSING>"
                else:
                    state = csz[1].split()[0]
                    zipp = csz[1].split()[-1]
            # print(city,state,zipp)
        elif len(add_list) ==5:
            if add_list[0] == " 3341 Lexington Road":
                continue
            else:
                location_name = add_list[0].strip()
                street_address = add_list[2].strip()
                city = add_list[3].split(',')[0].strip()
                state = add_list[3].split(',')[1].split()[0].strip()
                zipp = add_list[3].split(',')[1].split()[-1].strip()
        else:
            continue
        # print(zipp)
        # print(street_address +" | "+city+" | "+state+" | "+zipp +" | "+location_name)
        phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),info.split('message:')[-1])
        if phone_list !=[]:
            phone = phone_list[0].strip()
        else:
            phone = "<MISSING>"
        hours = " ".join(info.split('message:')[-1].split('<br />')[-2:]).split('<br>')

        if "Check for " in  " ".join(hours) or "Call for" in  " ".join(hours):
            hours_of_operation = "<MISSING>"
        else:
            # print(hours)
            # print(len(hours))
            # print('~~~~~~~~~~~~')


            if len(hours) ==2:
                hours_of_operation = hours[0].strip()
                # print(hours_of_operation)
            else:
                # print(hours)
                # print(len(hours))
                # print('~~~~~~~~~~~~')
                hours_list = hours[1].strip()
                # print(hours_list.split())
                if hours_list.split() != []:

                    if len(hours_list.split()) >1:
                        p =re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),str(hours_list))
                        if p ==[]  :
                            hours_of_operation = hours_list
                            # print(hours_of_operation)
                        else:
                            p1 = "".join(p)
                            # print(hours_list.split(p1))
                            h = hours_list.split(p1)[-1].split()
                            if h == []:
                                hours_of_operation = "<MISSING>"
                            else:
                                hours_of_operation = hours_list.split(p1)[-1].strip()
                                # print(hours_of_operation)

                    else:
                        hours_of_operation = "<MISSING>"
                else:
                    hours_of_operation = "<MISSING>"
        # print(hours_of_operation)

        if location_name == "Temecula - Promenade Mall" or location_name == "Victoria Gardens" or location_name == "Delaware":
            continue
        else:
            location_name = location_name.split("(")[0]
            street_address = street_address.replace(" (by Burt Bros.)","").replace(" (Fresh Market Parking Lot)","").replace("(Down East Lot)","").replace("(Near Honeybaked Ham) ","").replace("(Dominos Parking Lot) ","").replace("(Inside Walmart) ","").replace("  (Fresh Market)","").replace(" (Ft. Union Blvd)","")
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                    store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
            store = ["<MISSING>" if x == "" or x == None or x == "." else x for x in store]
            # if street_address in addresses:
        #     continue
        # addresses.append(street_address)

        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)



    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
