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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',

    }
  
    return_main_object=[]
  
    
        
    get_url= "http://shadehotel.com/"
    r = session.get(get_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")    
    main= soup.find_all("div",{"class":"shade-property"})
    for i in main:
        link = i.attrs['onclick'].split("('parent','")[1].split("/');")[0]
        r1 = session.get(link,headers=headers)
        soup1= BeautifulSoup(r1.text,"lxml")
        location_name= soup1.find("h1",{"home-headline"}).text            
        main1= soup1.find("div",{"class":"c2"})
        st =list(main1.stripped_strings)
        address =st[1]
        city_tmp =st[2].split(',')
        city = city_tmp[0]
        state_tmp = city_tmp[1].strip().split(' ')
        state = state_tmp[0]
        zip =state_tmp[1]
        phone = st[4].strip()
        hour_tmp= soup1.find("div",{"class":"c3"})
        hour =" ".join(list(hour_tmp.stripped_strings)).strip()

 
        tem_var =[]
        tem_var.append(get_url)
        tem_var.append(location_name)
        tem_var.append(address)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hour.strip())
        tem_var.append(link)
        return_main_object.append(tem_var)
 


    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


