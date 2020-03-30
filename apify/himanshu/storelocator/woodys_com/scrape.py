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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url= "https://woodys.com/locations/"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    k = soup.find_all("div",{"class":"et_pb_text_inner"})
    hours =[]
    lat =[]
    lng =[]
    url =[]
    for i in k:
        a =i.find_all("a")
        for j in a:
            if "https:" in j['href']:
                store_name.append(j.text)
                r = session.get(j['href'],headers=headers)
                soup1= BeautifulSoup(r.text,"lxml")
                lat.append(soup1.find("div",{"class":"et_pb_map_pin"}).attrs['data-lat'])
                lng.append(soup1.find("div",{"class":"et_pb_map_pin"}).attrs['data-lng'])
                k = (soup1.find_all("div",{"class":"et_pb_text_align_left"}))
                url.append(j['href'])
                for i in k:
                    st =  i.find_all("div",{"class":"et_pb_text_inner"})
                    for i in st:
                        tem_var =[]
                        if "Phone:" in list(i.stripped_strings) or "Phone" in list(i.stripped_strings):
                            street_address = list(i.stripped_strings)[0]
                            city  =list(i.stripped_strings)[1].split(',')[0]
                            state =list(i.stripped_strings)[1].split(',')[1].split( )[0]
                            zipcode = list(i.stripped_strings)[1].split(',')[1].split( )[1]

                            phone  = (list(i.stripped_strings)[-1])
                            new_list =list(i.stripped_strings)[2:5]
                            patt = re.compile(r'[0-9-\(\) ]+$')
                            if patt.match(new_list[-1]):
                                del new_list[-1]
                            hours.append(" ".join(new_list).replace("Phone:","").replace("Phone","").replace("Trivia Night Wednesdays starting August 29th",""))


                            tem_var.append(street_address)
                            tem_var.append(city)
                            tem_var.append(state.strip())
                            tem_var.append(zipcode.strip())
                            tem_var.append("US")
                            tem_var.append("<MISSING>")
                            tem_var.append(phone)
                            tem_var.append("<MISSING>")
                            # tem_var.append("<MISSING>")
                            # tem_var.append("<MISSING>")
                            # tem_var.append(hours)
                            # tem_var.append(j['href'])
                            store_detail.append(tem_var)
      
                
    for i in range(len(store_name)):
        store = list()
        store.append("https://woodys.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append(lat[i])
        store.append(lng[i])
        store.append(hours[i])
        store.append(url[i])
        return_main_object.append(store) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


