import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://storelocator.officedepot.com/ajax?&xml_request=%3Crequest%3E%3Cappkey%3EAC2AD3C2-C08F-11E1-8600-DCAD4D48D7F4%3C%2Fappkey%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Climit%3E250%3C%2Flimit%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3E33496%3C%2Faddressline%3E%3Clongitude%3E-80.15960410000002%3C%2Flongitude%3E%3Clatitude%3E26.4039904%3C%2Flatitude%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Csearchradius%3E20%7C35%7C50%7C100%7C250%3C%2Fsearchradius%3E%3Cwhere%3E%3Cor%3E%3Cnowdocs%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fnowdocs%3E%3Cexpanded_furn%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fexpanded_furn%3E%3Cusps%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fusps%3E%3Cshredding%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fshredding%3E%3Cselfservews%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fselfservews%3E%3Cphotoprint%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fphotoprint%3E%3Cexpandedbb%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fexpandedbb%3E%3Cwarranty_carry%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fwarranty_carry%3E%3Ccellphonerepair%3E%3Cin%3E%3C%2Fin%3E%3C%2Fcellphonerepair%3E%3Ctechtradein%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ftechtradein%3E%3Ctechrecycling%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ftechrecycling%3E%3Ctechzone%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ftechzone%3E%3Cselfservprinting%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fselfservprinting%3E%3Cusps_mail%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fusps_mail%3E%3C%2For%3E%3Cicon%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ficon%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    return_main_object =[]
    store_detail =[]
    store_name=[]
    tem_var =[]
    names =  soup.find_all("address2")
    address1 = soup.find_all("address1")
    state1 = soup.find_all("state")
    city1 = soup.find_all("city")
    postalcode1= soup.find_all("postalcode")
    countrys =  soup.find_all('country')
    store_no1 = soup.find_all("clientkey")
    phones = soup.find_all('phone')
    latitude1 = soup.find_all("latitude")
    longitude1 = soup.find_all("longitude")
    
    address2=[]
    city2=[]
    state2 =[]
    postalcode2=[]
    country2=[]
    store_no2=[]
    phone2=[]
    latitude2=[]
    longitude2=[]
    
    mons2=[]
    tuess2=[]
    wed2=[]
    thu2=[]
    fri2=[]
    sat2=[]
    sun2=[]
    hours2=[]
    mons = soup.find_all("mon")
    tuess = soup.find_all("tues")
    wed1 = soup.find_all("wed")
    thu1 =  soup.find_all("thur")
    fri1 = soup.find_all("fri")
    sat1 = soup.find_all("sat")
    sun1 = soup.find_all("sun")
  

    for mon in mons:
        mons2.append(mon.text)
    
    for tues in tuess:
        tuess2.append(tues.text)

    for wed in  wed1:
        wed2.append(wed.text)

    for thu in thu1:
        thu2.append(thu.text)

    for fri in fri1:
        fri2.append(fri.text)
        
        
    for sat in sat1:
        sat2.append(sat.text)

    for sun in sun1:
        sun2.append(sun.text)

    for j in range(len(mons2)):
        hours=''
        time =[]
        time.append(mons2[j])
        time.append(tuess2[j])
        time.append(wed2[j])
        time.append(thu2[j])
        time.append(fri2[j])
        time.append(sat2[j])
        time.append(sun2[j])
        for i in time:
            hours = hours+ ' ' +i
        hours2.append(hours)
    

    for address in address1:
        address2.append(address.text)

    for city in city1:
        city2.append(city.text)


    for state in state1:
        state2.append(state.text)

    for postalcode in postalcode1:
        postalcode2.append(postalcode.text)

    for country in countrys:
        country2.append(country.text)
    
    for store_no in store_no1:
        store_no2.append(store_no.text)
    
    
    for phone in phones:
        phone2.append(phone.text)
    
    for latitude in latitude1:
        latitude2.append(latitude.text)

    for longitude in longitude1:
        longitude2.append(longitude.text)

    for add in names:
        store_name.append(add.text)
    

    for i in range(len(address2)):
        new_list=[]
        new_list.append(address2[i])
        new_list.append(city2[i])
        new_list.append(state2[i])
        new_list.append(postalcode2[i])
        new_list.append(country2[i])
        new_list.append(store_no2[i])
        new_list.append(phone2[i])
        new_list.append("officedepot")
        new_list.append(latitude2[i])
        new_list.append(longitude2[i])
        new_list.append(hours2[i])
        store_detail.append(new_list)


    store_name[15] ='1570 N FEDERAL HWY'
    

    for i in range(len(store_name)):
        store = list()
        store.append("https://www.officedepot.com")  
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
    

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
