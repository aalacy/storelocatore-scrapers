import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.columbiabank.com"
    r = session.get("https://hosted.where2getit.com/columbiabank/indexsecure-t13289.html")
    soup = BeautifulSoup(r.text,"lxml")
    app_key = soup.find("appkey").text
    states_reqeust = session.get("https://hosted.where2getit.com/columbiabank/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E" + str(app_key)+ "%3C%2Fappkey%3E%3Cformdata+id%3D%22getlist%22%3E%3Cobjectname%3EAccount%3A%3AState%3C%2Fobjectname%3E%3Cwhere%3E%3Ccountry%3EUS%3C%2Fcountry%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E")
    states_soup = BeautifulSoup(states_reqeust.text,"lxml")
    return_main_object = []
    for state in states_soup.find_all("name"):
        location_request = session.get("https://hosted.where2getit.com/columbiabank/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E" + str(app_key) + "%3C%2Fappkey%3E%3Cgeoip%3E1%3C%2Fgeoip%3E%3Cformdata+id%3D%22getlist%22%3E%3Cobjectname%3EStoreLocator%3C%2Fobjectname%3E%3Corder%3ECITY%3C%2Forder%3E%3Cwhere%3E%3Cand%3E%3Cstate%3E%3Ceq%3E"+ str(state.text) +"%3C%2Feq%3E%3C%2Fstate%3E%3Cor%3E%3Cdriveupbank%3E%3Cilike%3E%3C%2Filike%3E%3C%2Fdriveupbank%3E%3Cwalkupatm%3E%3Cilike%3E%3C%2Filike%3E%3C%2Fwalkupatm%3E%3Cdriveupatm%3E%3Cilike%3E%3C%2Filike%3E%3C%2Fdriveupatm%3E%3Catmacceptsdeposits%3E%3Cilike%3E%3C%2Filike%3E%3C%2Fatmacceptsdeposits%3E%3Cnightdeposits%3E%3Cilike%3E%3C%2Filike%3E%3C%2Fnightdeposits%3E%3Csafedepoistbox%3E%3Cilike%3E%3C%2Filike%3E%3C%2Fsafedepoistbox%3E%3Ccashmgt%3E%3Cilike%3E%3C%2Filike%3E%3C%2Fcashmgt%3E%3Cresidentiallending%3E%3Cilike%3E%3C%2Filike%3E%3C%2Fresidentiallending%3E%3Cinlbanking%3E%3Cilike%3E%3C%2Filike%3E%3C%2Finlbanking%3E%3Cprofessionalbanking%3E%3Cilike%3E%3C%2Filike%3E%3C%2Fprofessionalbanking%3E%3Ctrustservices%3E%3Cilike%3E%3C%2Filike%3E%3C%2Ftrustservices%3E%3Ccbfinancialservices%3E%3Cilike%3E%3C%2Filike%3E%3C%2Fcbfinancialservices%3E%3Cprivatebanking%3E%3Cilike%3E%3C%2Filike%3E%3C%2Fprivatebanking%3E%3Ccommericallending%3E%3Cilike%3E%3C%2Filike%3E%3C%2Fcommericallending%3E%3Copen_weekends%3E%3Cin%3E%3C%2Fin%3E%3C%2Fopen_weekends%3E%3C%2For%3E%3C%2Fand%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E")
        lcoation_soup = BeautifulSoup(location_request.text,"lxml")
        for location in lcoation_soup.find_all("poi"):
            name = location.find("name").text
            address1 = location.find("address1").text
            address2 = location.find("address2")
            if address2 == None:
                address = address1
            else:
                address = address1 + address2.text
            city = location.find("city").text
            state = location.find("state").text
            zip_code = location.find("postalcode").text
            phone = location.find("phone").text
            latitude = location.find("latitude").text
            longitude = location.find("longitude").text
            hours = ""
            store_hours = []
            store_hours.append(location.find("dhmonday"))
            store_hours.append(location.find("dhtuesday"))
            store_hours.append(location.find("dhwednesday"))
            store_hours.append(location.find("dhthursday"))
            store_hours.append(location.find("dhfriday"))
            store_hours.append(location.find("dhsaturday"))
            store_hours.append(location.find("dhsunday"))
            days =  {0: "Monday",1:"Tuesday",2:"Wednesday",3:"Thursday",4:"Friday",5:"Saturday",6:"Sunday"}
            for k in range(len(store_hours)):
                if store_hours[k].text != "":
                    hours = hours + " " + days[k] + " " + store_hours[k].text
            store = []
            store.append("https://www.columbiabank.com")
            store.append(name)
            store.append(address)
            store.append(city)
            store.append(state)
            store.append(zip_code)
            store.append("US")  
            store.append("<MISSING>")
            store.append(phone if phone != "" else "<MISSING>")
            store.append("columbian bank")
            store.append(latitude)
            store.append(longitude)
            store.append(hours if hours != "" else "<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
