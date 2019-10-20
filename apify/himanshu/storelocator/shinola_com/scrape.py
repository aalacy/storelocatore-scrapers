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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    return_main_object=[]
    name_store=[]
    store_detail=[]
    addresses = []
   
    base_url= "https://www.shinola.com/store-locator"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    vk = soup.find('div',{'id':'amazon-root'}).find_next('script').find_next('script').text.split('"stores":')[1].split(',"total"')[0]

    k = json.loads(vk)
    
        
    for idx, val in enumerate(k):
        
        tem_var=[]
        locator_domain = "https://www.shinola.com"
        location_name = val["name"]
        zipcode = (val['zipcode'])        
        phone = (val['phone'])
        street = val['address']
        city = val['city']
        country = val['country']
        state = val['state']
        hours = 'monday'+' '+val['monday_open'] +' ' + val['monday_close'] + ' '+ 'tuesday'+' '+ val['tuesday_open']+ ' '+ val['tuesday_close'] + ' '+ ' wednesday'+' ' +val['wednesday_open'] +' '+ val['wednesday_close'] +' ' +' thursday'+' '+ val['thursday_open'] +' '+ val['thursday_close']+ ' '+ 'friday'+' '+val['friday_open']+' '+val['friday_close']+' '+'saturday'+' '+val['saturday_open']+' '+val['saturday_close']+ ' '+'sunday'+' '+ val['sunday_open']+' '+val['sunday_close']
        page_url = "https://www.shinola.com/store-locator"
        if street in addresses:
                continue
        addresses.append(street)
        latitude = val['latitude']
        longitute = val['longtitude']
        tem_var.append( locator_domain if locator_domain else "<MISSING>" )
        tem_var.append( location_name if location_name else "<MISSING>" )
        tem_var.append( street if street else "<MISSING>" )
        tem_var.append( city if city else "<MISSING>" )
        tem_var.append( state if state else "<MISSING>" )
        tem_var.append( zipcode if zipcode else "<MISSING>" )
        tem_var.append( country if country else "<MISSING>" )
        tem_var.append("<MISSING>")
        tem_var.append( phone if phone else "<MISSING>" )
        tem_var.append("<MISSING>")
       
        tem_var.append(latitude)
        tem_var.append(longitute)
        tem_var.append(hours)
        tem_var.append(page_url)
        store_detail.append(tem_var)

        print("data====",str(tem_var))
        yield tem_var
        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


