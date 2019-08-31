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

    return_main_object=[]
    name_store=[]
    store_detail=[]
    for loop in range(0,20):
        base_url= "https://www.shinola.com/shinstorelocator/index/searchlocation/?location=&shinolaStoresCurrentPage=0&authorizedRetailersCurrentPage="+str(loop)
        r = requests.get(base_url)
        soup= BeautifulSoup(r.text,"lxml")
        
        k = json.loads(soup.text)
        
        if loop==0:
            for idx, val in enumerate(k['shinola_stores']):
                
                tem_var=[]
                name_store.append(val["name"])
                zipcode = (val['postcode'])
                
                phone = (val['phone'])
                street = val['street']
                city = val['city']
                country = val['country']
                state = val['region']
                hours = 'monday'+' '+val['monday_open'] +' ' + val['monday_close'] + ' '+ 'tuesday'+' '+ val['tuesday_open']+ ' '+ val['tuesday_close'] + ' '+ ' wednesday'+' ' +val['wednesday_open'] +' '+ val['wednesday_close'] +' ' +' thursday'+' '+ val['thursday_open'] +' '+ val['thursday_close']+ ' '+ 'friday'+' '+val['friday_open']+' '+val['friday_close']+' '+'saturday'+' '+val['saturday_open']+' '+val['saturday_close']+ ' '+'sunday'+' '+ val['sunday_open']+' '+val['sunday_close']

                tem_var.append( street if street else "<MISSING>" )
                tem_var.append( city if city else "<MISSING>" )
                tem_var.append( state if state else "<MISSING>" )
                tem_var.append( zipcode if zipcode else "<MISSING>" )
                tem_var.append( country if country else "<MISSING>" )
                tem_var.append("<MISSING>")
                tem_var.append( phone if phone else "<MISSING>" )
                tem_var.append("shinola")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(hours)
                store_detail.append(tem_var)

        for idx, val in enumerate(k['authorized_retailers']):
            tem_var=[]
            # zipcode=''
            name_store.append(val["name"])
            zipcode1 = val['postcode']
            # print(len(zipcode))
            phone = (val['phone'])
            street = val['street']
            city = val['city']
            country = val['country']
            state = val['region']

            if "40 Monroe Center #103" in street:
                street = (street.replace("40 Monroe Center #103","103 Monroe Center"))

            if "Somerset Collection" in street:
        
                street =city.split('.')[0]
                city = city.split('.')[1]
                
                tem_var.append( street if street else "<MISSING>" )
                tem_var.append( city if city else "<MISSING>" )
            else:
                tem_var.append( street if street else "<MISSING>" )
                tem_var.append( city if city else "<MISSING>" )


            if zipcode1:
                if len(zipcode1)==4:
                    zipcode = str(0)+zipcode1
                else:
                    zipcode = zipcode1
              


            tem_var.append( state if state else "<MISSING>" )
            tem_var.append( zipcode.replace("Mati","").replace("24B","<MISSING>").replace("918","<MISSING>") if zipcode else "<MISSING>" )
            tem_var.append( country if country else "<MISSING>" )
            tem_var.append("<MISSING>")
            tem_var.append( phone.replace(", (905) 4","").replace("(0155) 5518 1313","") if phone else "<MISSING>" )
            tem_var.append("shinola")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            store_detail.append(tem_var) 
    

    for i in range(len(name_store)):
        store = list()
        store.append("https://www.shinola.com")
        store.append(name_store[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
            
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
