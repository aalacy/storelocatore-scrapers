import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



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

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url= "https://primosmex.com/locations/"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    k = soup.find_all("div",{'class':"fl-row-content-wrap"})
  
    k1 = soup.find_all("div",{'class':"uabb-infobox-text uabb-text-editor"})
    # for i in k:
        
    #     k1 = soup.find_all("div",{'class':"uabb-infobox-text uabb-text-editor"})
    k2 = soup.find_all("div",{'class':"uabb-infobox-title-wrap"})


    for index,j in enumerate(k2):
        
        if "ORANGE COUNTY" in list(j.stripped_strings)[0] or "SAN DIEGO COUNTY" in list(j.stripped_strings)[0] or "INLAND EMPIRE" in list(j.stripped_strings)[0]:
            pass
        else:
            store_name.append(list(j.stripped_strings)[0])
    
    for index,j in enumerate(k1):
        tem_var=[]
        st = list(j.stripped_strings)[0]
        city = list(j.stripped_strings)[1].split(',')[0]
        state = list(j.stripped_strings)[1].split(',')[1].split( )[0]
        zip1 = (list(j.stripped_strings)[1].split(',')[1].split( )[1])
        phone = list(j.stripped_strings)[2]
        hours = " ".join(list(j.stripped_strings)[5:])
        

        tem_var.append("https://www.primosmex.com")
        tem_var.append(store_name[index])
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state.replace("44256","<MISSING>"))
        tem_var.append(zip1)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("primosmex")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hours)
        return_main_object.append(tem_var)

  
    
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


