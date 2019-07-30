import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.truereligion.com"
    r = requests.get('https://hosted.where2getit.com/truereligion/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E1C4F6E2A-C3CC-11E2-A252-16BE05D25870%3C%2Fappkey%3E%3Cgeoip%3E1%3C%2Fgeoip%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Climit%3E250%3C%2Flimit%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3EEnter+address%2C+city+%26+state+or+postalcode%3C%2Faddressline%3E%3Clongitude%3E%3C%2Flongitude%3E%3Clatitude%3E%3C%2Flatitude%3E%3Ccountry%3E%3C%2Fcountry%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Csearchradius%3E50%7C100%7C250%7C500%3C%2Fsearchradius%3E%3Cwhere%3E%3Cor%3E%3Coutlet%3E%3Ceq%3E%3C%2Feq%3E%3C%2Foutlet%3E%3Cfullprice%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ffullprice%3E%3Cbespoke%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fbespoke%3E%3Cinternationalwholesale%3E%3Ceq%3E%3C%2Feq%3E%3C%2Finternationalwholesale%3E%3C%2For%3E%3Cclientkey%3E%3Cnotin%3ETRHB-2262EVAVC%2CTRHB-5233AAVC%3C%2Fnotin%3E%3C%2Fclientkey%3E%3C%2Fwhere%3E%3Cstateonly%3E1%3C%2Fstateonly%3E%3C%2Fformdata%3E%3C%2Frequest%3E')
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    output=[]
    main=soup.find_all('poi')
    for poi in main:
        name=poi.find('name').text.strip()
        address=poi.find('address1').text.strip()
        storeno=poi.find('address2').text.strip()
        city=poi.find('city').text.strip()
        country=poi.find('country').text.strip()
        state=poi.find('state').text.strip()
        lat=poi.find('latitude').text.strip()
        lng=poi.find('longitude').text.strip()
        phone=poi.find('phone').text.strip()
        zip=poi.find('postalcode').text.strip()
        hour=''
        if poi.find('monopen').text.strip():
            hour+=" Monday : "+poi.find('monopen').text.strip()+poi.find('monclose').text.strip()
        if poi.find('tueopen').text.strip():
            hour+=" Tuesday : "+poi.find('tueopen').text.strip()+poi.find('tueclose').text.strip()
        if poi.find('wedopen').text.strip():
            hour+=" Wednesday : "+poi.find('wedopen').text.strip()+poi.find('wedclose').text.strip()
        if poi.find('thropen').text.strip():
            hour+=" Thursday : "+poi.find('thropen').text.strip()+poi.find('thrclose').text.strip()
        if poi.find('friopen').text.strip():
            hour+=" Friday : "+poi.find('friopen').text.strip()+poi.find('friclose').text.strip()
        if poi.find('satopen').text.strip():
            hour+=" Saturday : "+poi.find('satopen').text.strip()+poi.find('satclose').text.strip()
        if poi.find('sunopen').text.strip():
            hour+=" Sunday : "+poi.find('sunopen').text.strip()+poi.find('sunclose').text.strip()
        store=[]
        store.append(base_url)
        store.append(name if name else "<MISSING>")
        store.append(address if address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zip if zip else "<MISSING>")
        store.append(country if country else "<MISSING>")
        store.append(storeno if storeno else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("truereligion")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        if zip not in output:
            output.append(zip)
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
