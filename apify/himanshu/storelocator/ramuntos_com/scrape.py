import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from collections import OrderedDict 
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ramuntos_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url= "https://ramuntos.com/locations/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")

    k=soup.find_all("div",{"class":"entry-content"})
    for j in range(1,12):
        k1 = soup.find("div",{'class':"et_pb_row et_pb_row_"+str(j)})
        # name = list(k1.stripped_strings)[0]
        v = list(k1.stripped_strings)
        tem_var =[]
        if "(Jiffy Mart)" in v:
            
            lat = (k1.find("div",{"class":"et_pb_map_pin"}).attrs['data-lat'])
            lng = (k1.find("div",{"class":"et_pb_map_pin"}).attrs['data-lng'])
            phone = (v[-3].replace("\xa0","").replace("Phone:",""))
            hours = (v[-4])
            city = v[3].split(",")[0]
            state = v[3].split(",")[1].split( )[0]
            state = v[3].split(",")[1].split( )[0]
            zip1 = v[3].split(",")[1].split( )[1]
            st = v[2]
            name = (" ".join(v[:2]))
        else:
            if len(v)==7:
                lat = (k1.find("div",{"class":"et_pb_map_pin"}).attrs['data-lat'])
                lng = (k1.find("div",{"class":"et_pb_map_pin"}).attrs['data-lng'])
                st=v[1]
                name = v[0]
                city = v[2].split(',')[0]
                state = v[2].split(',')[1].split( )[0]
                zip1 = v[2].split(',')[1].split( )[1]
                hours = v[3]
                phone = v[-2]
                # logger.info(lat)
                # logger.info("=====7",zip1)
            elif len(v)==9:
                lat = (k1.find("div",{"class":"et_pb_map_pin"}).attrs['data-lat'])
                lng = (k1.find("div",{"class":"et_pb_map_pin"}).attrs['data-lng'])
                name = v[0]
                st = v[1]
                city = v[2].split(',')[1]
                state = v[2].split(',')[1].split( )[0]
                zip1 = v[2].split(',')[1].split( )[1]
                hours = (" ".join(v[3:7]))
                phone = v[-2]
                # logger.info(lat)
                # logger.info("=====9",zip1)

            elif len(v)==6:
                lat = (k1.find("div",{"class":"et_pb_map_pin"}).attrs['data-lat'])
                lng = (k1.find("div",{"class":"et_pb_map_pin"}).attrs['data-lng'])
                name = v[0]
                st = v[1].split(',')[0]
                city = v[1].split(',')[1]
                state = v[1].split(',')[2].split( )[0]
                zip1 = v[1].split(',')[2].split( )[1]
                hours = v[2]
                phone = v[4]
                # logger.info(v[1].split(',')[2].split( )[0])
                # logger.info(lat)
                # logger.info("=====6",zip1)
               
            elif len(v)==8:
                lat = (k1.find("div",{"class":"et_pb_map_pin"}).attrs['data-lat'])
                lng = (k1.find("div",{"class":"et_pb_map_pin"}).attrs['data-lng'])
                name = v[0]
                # logger.info(v)
                st = v[1].split(',')[0]
                city = v[2].split(',')[0]
                state = v[2].split(',')[1].split( )[0]
                zip1 = v[2].split(',')[1].split( )[1]
                hours = v[3]
                phone = v[5]
                # logger.info(lat)
                # logger.info("=====8",zip1)
        tem_var.append("https://ramuntos.com")
        tem_var.append(name)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone.replace("Phone: ",""))
        tem_var.append("ramuntos")
        tem_var.append(lat)
        tem_var.append(lng)
        tem_var.append(hours)
        tem_var.append("https://ramuntos.com/locations/")
        if "519 Main Street" in tem_var:
            tem_var[-2] = hours[-2].replace("0","Open 7 days a week. Mon – Thurs: 11am – 10pm Friday & Saturday: 11am – 11pm Sunday: 11am – 9pm")

        
        yield tem_var
        # store_detail.append(tem_var) 
                

    # return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


