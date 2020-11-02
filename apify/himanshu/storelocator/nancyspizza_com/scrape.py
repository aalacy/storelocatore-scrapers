import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('nancyspizza_com')





session = SgRequests()

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
  
    base_url= "https://api.storepoint.co/v1/15946036157640205728661006/locations?rq"
    r = session.get(base_url).json()
    
    store_name=[]
    store_detail=[]
    return_main_object=[]
    for idx, val in enumerate(r['results']['locations']):
        latitude = val['loc_lat']
        longitude =val['loc_long']
        phone = val['phone']
        # logger.info(val)
        hours = ( 'monday'+' '+val['monday'] + ' tuesday ' +val['tuesday']+' wednesday ' +val['wednesday']+' thursday ' + val['thursday']+ ' friday '+val['friday']+ ' saturday ' +val['saturday']+ ' sunday ' +val['sunday'])

        store_name.append(val['name'])

        tem_var=[]
        if len(val['streetaddress'].split(',')) !=1:
            if (len(val['streetaddress'].split(','))) ==3:
                street_address = (val['streetaddress'].split(',')[0])
                city = val['streetaddress'].split(',')[1]
                state= val['streetaddress'].split(',')[2].split( )[0]
                zipcode = val['streetaddress'].split(',')[2].split( )[1]
                
                tem_var.append(street_address)
                tem_var.append(city)
                tem_var.append(state.strip())
                tem_var.append(zipcode.strip())
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("nancyspizza")
                tem_var.append(latitude)
                tem_var.append(longitude)
                tem_var.append(hours)

                store_detail.append(tem_var)
            
            elif (len(val['streetaddress'].split(','))) ==4:
                if "5805 State Bridge Road" in val['streetaddress'].split(','):
                    street_address = val['streetaddress'].split(',')[0]
                    city = val['streetaddress'].split(',')[1]
                    state = val['streetaddress'].split(',')[2]
                    zipcode =  val['streetaddress'].split(',')[3]

                    tem_var.append(street_address)
                    tem_var.append(city)
                    tem_var.append(state.strip())
                    tem_var.append(zipcode.strip())
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("nancyspizza")
                    tem_var.append(latitude)
                    tem_var.append(longitude)
                    tem_var.append(hours)
                    
                    store_detail.append(tem_var)
                   
                else:
                    street_address = " ".join(val['streetaddress'].split(',')[:2])
                    city = (val['streetaddress'].split(',')[2])
                    state = (val['streetaddress'].split(',')[3]).split( )[0]
                    zipcode =  (val['streetaddress'].split(',')[3]).split( )[1]

                    tem_var.append(street_address)
                    tem_var.append(city)
                    tem_var.append(state.strip())
                    tem_var.append(zipcode.strip())
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("nancyspizza")
                    tem_var.append(latitude)
                    tem_var.append(longitude)
                    tem_var.append(hours)

                    store_detail.append(tem_var)
            
            elif (len(val['streetaddress'].split(','))) ==2:
                street_address = " ".join(val['streetaddress'].split(',')[0].split('.')[:2])
                city = val['streetaddress'].split(',')[0].split('.')[2]
                state = val['streetaddress'].split(',')[1].split( )[0]
                zipcode =  val['streetaddress'].split(',')[1].split( )[1]

                tem_var.append(street_address)
                tem_var.append(city)
                tem_var.append(state.strip())
                tem_var.append(zipcode.strip())
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("nancyspizza")
                tem_var.append(latitude)
                tem_var.append(longitude)
                tem_var.append(hours)

                store_detail.append(tem_var)

        else:
            street_address = (" ".join(val['streetaddress'].split( )[:4]))
            
            city = 'Atlanta'
            state = "GA"
            zipcode =  val['streetaddress'].split( )[4]

            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state.strip())
            tem_var.append(zipcode.strip())
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("nancyspizza")
            tem_var.append(latitude)
            tem_var.append(longitude)
            tem_var.append(hours)

            store_detail.append(tem_var)
            
            
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.nancyspizza.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        logger.info(store)
        return_main_object.append(store)
        
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


