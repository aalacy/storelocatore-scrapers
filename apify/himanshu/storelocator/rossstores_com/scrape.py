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
    base_url= "https://hosted.where2getit.com/rossdressforless/2014/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E097D3C64-7006-11E8-9405-6974C403F339%3C%2Fappkey%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Climit%3E20%3C%2Flimit%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3E67205%3C%2Faddressline%3E%3Clongitude%3E%3C%2Flongitude%3E%3Clatitude%3E%3C%2Flatitude%3E%3Ccountry%3EUS%3C%2Fcountry%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Csearchradius%3E100%7C250%3C%2Fsearchradius%3E%3Cwhere%3E%3Cclientkey%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fclientkey%3E%3Copendate%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fopendate%3E%3Cshopping_spree%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fshopping_spree%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    

    monday=soup.find_all("monday")
    tuesday=soup.find_all("tuesday")
    wednesday=soup.find_all("wednesday")
    thursday=soup.find_all("thursday")
    friday = soup.find_all("friday")
    saturday=soup.find_all("saturday")
    sunday=soup.find_all("sunday")
    # print(soup.find_all("friday"))
    st1 = soup.find_all("address1")
    city1 = soup.find_all("city")
    state1 = soup.find_all("state")
    name1 = soup.find_all("name")
    phone1 = soup.find_all("phone")
    postalcode1= soup.find_all("postalcode")
    latitude1 = soup.find_all("latitude")
    longitude1 = soup.find_all("longitude")
    
    
    for index,i in enumerate(st1):
        tem_var=[]
        hours = (monday[index].text + ' ' + tuesday[index].text + ' '+wednesday[index].text + ' '+ thursday[index].text + ' ' +friday[index].text + ' '+ saturday[index].text+ ' '+sunday[index].text)

        tem_var.append("https://www.rossstores.com")
        tem_var.append(name1[index].text)
        tem_var.append(st1[index].text)
        tem_var.append(city1[index].text)
        tem_var.append(state1[index].text)
        tem_var.append(postalcode1[index].text)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("rossstores")
        tem_var.append(latitude1[index].text)
        tem_var.append(longitude1[index].text)
        tem_var.append(hours)

        return_main_object.append(tem_var) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


