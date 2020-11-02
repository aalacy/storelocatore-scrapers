import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('johnstonmurphy_com')






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


def minute_to_hours(time):
    am = "AM"
    hour = int(time / 60)
    if hour > 12:
        am = "PM"
        hour = hour - 12
    if int(str(time / 60).split(".")[1]) == 0:
        
        return str(hour) + ":00" + " " + am
        
    else:
        k1 = str(int(str(time / 60).split(".")[1]) * 6)[:2]
        return str(hour) + ":" + k1 + " " + am
        


def fetch_data():
    zips = sgzip.for_radius(100)
    # zips =sgzip.coords_for_radius(50)
    return_main_object = []
    addresses = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',

    }

    # it will used in store data.
    for zip_code in zips:
        try:
            r = session.get(
            'https://www.johnstonmurphy.com/on/demandware.store/Sites-johnston-murphy-us-Site/en_US/Stores-FindStores?dwfrm_storelocator_countryCode=US&dwfrm_storelocator_distanceUnit=mi&dwfrm_storelocator_postalCode='+zip_code+'&dwfrm_storelocator_maxdistance=30000&dwfrm_storelocator_findbyzip=Search',
            headers=headers)
        except:
            pass
        soup1= BeautifulSoup(r.text,"lxml")

        k = (soup1.find_all("div",{"class":"store-name"}))      
        p=0
        for i in k:
            tem_var =[]
            if len(list(i.stripped_strings))!=5:
                if len(list(i.stripped_strings))==8:
                    name = list(i.stripped_strings)[0]
                    st = list(i.stripped_strings)[1]
                    city = list(i.stripped_strings)[2].split(',')[0]
                    state = list(i.stripped_strings)[2].split(',')[1].split( )[0]
                    zip1 = " ".join(list(i.stripped_strings)[2].split(',')[1].split( )[1:])
                    phone  = list(i.stripped_strings)[4]
                    h1 = " ".join(list(i.stripped_strings)[5:]).replace("Directions","").replace("Hours:&nbsp","")
                    if h1:
                        time = (h1)
                    else:
                        time = "<MISSING>"
                else:
                    name = list(i.stripped_strings)[0]
                    st = list(i.stripped_strings)[1]
                    city = list(i.stripped_strings)[2].split(',')[0]
                    if len(list(i.stripped_strings)[2].split(',')[1].split( ))==1:
                        state = list(i.stripped_strings)[2].split(',')[1].split( )[0]
                        # logger.info(list(i.stripped_strings)[2].split(',')[1].split( ))
                    else:
                        if len(list(i.stripped_strings)[2].split(',')[1].split( )[-1])==3:
                            zip1 = " ".join(list(i.stripped_strings)[2].split(',')[1].split( )[-2:])
                            state = (list(i.stripped_strings)[2].split(',')[1].split( )[-3])

                        else:
                            city = list(i.stripped_strings)[2].split(',')[0]
                            zip1 = list(i.stripped_strings)[2].split(',')[1].split( )[-1]
                            state = " ".join(list(i.stripped_strings)[2].split(',')[1].split( )[:-1])
                            # logger.info(" ".join(list(i.stripped_strings)[2].split(',')[1].split( )[:-1]))
            else:
                name = list(i.stripped_strings)[0]
                if len(list(i.stripped_strings)[2].split(","))==2:
                    st = list(i.stripped_strings)[1]
                    city = list(i.stripped_strings)[2].split(",")[0]
                    state = list(i.stripped_strings)[2].split(",")[1].split( )[0]
                    zip1 = " ".join(list(i.stripped_strings)[2].split(",")[1].split( )[1:])
                    phone = "<MISSING>"
                else:
                    st = list(i.stripped_strings)[1]
                    city = list(i.stripped_strings)[1].split(",")[0]
                    state = list(i.stripped_strings)[1].split(",")[1].split( )[0]
                    zip1 = " ".join(list(i.stripped_strings)[1].split(",")[1].split( )[1:])
                    phone  = "<MISSING>"
                    
                    # logger.info(" ".join(list(i.stripped_strings)[1].split(",")[1].split( )[1:]))
                
            
            tem_var.append("https://www.johnstonmurphy.com")
            tem_var.append(name.replace(u'\xe9', u' ') if name else "<MISSING>")
            tem_var.append(st.replace("CA","").replace("(WI)","")  if st else "<MISSING>")
            tem_var.append(city  if city else "<MISSING>")
            tem_var.append(state.replace("Panama","<MISSING>").replace(u'\xe9', u' ').replace(u'\xf3', u' ').replace("Estado de M xico","MS") if state.replace("Panama","<MISSING>").replace(u'\xe9', u' ').replace(u'\xf3', u' ') else "<MISSING>")
            if len(zip1)==6 or len(zip1)==7:
                c = 'CA'
            else:
                c = "US"
            tem_var.append(zip1.replace("City","") if zip1.replace("City","") else "<MISSING>")
            tem_var.append(c)
            tem_var.append("<MISSING>")
            tem_var.append(phone if phone  else "<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<INACCESSIBLE>" )
            tem_var.append("<INACCESSIBLE>")
            tem_var.append(time.replace(u'\u2013', u' ') if time.replace(u'\u2013', u' ')  else "<MISSING>" )
            tem_var.append('<MISSING>')
            if tem_var[3] not in addresses:
                addresses.append(tem_var[3])
                #logger.info(tem_var)
                yield tem_var
        # exit()
    


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
