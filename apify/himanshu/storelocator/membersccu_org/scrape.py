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
    base_url= "https://www.membersccu.org/hours-and-locations"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    lat =[]
    lng =[]
    k1 = soup.find_all("script")



    for i in k1:
        if "var markers" in i.text:
            for index,j in enumerate(i.text.split("onClick='getDir"),start=0):
                if index !=0:
                    lat.append(i.text.split("onClick='getDir")[index].split(");'")[0].replace("(","").split(",")[0])
                    lng.append(i.text.split("onClick='getDir")[index].split(");'")[0].replace("(","").split(",")[1])
    k= soup.find_all("div",{"class":"liner"})
    kk = soup.find('div', {'class': 'pinned'}).find_next('script').text.split('var point = new google.maps.LatLng')
    main = []
    for key, val in enumerate(kk):
        if key != 0:
            bb = val.split(';')[0].replace(')', '').replace('(', '').strip(',')
            if bb in main:
                continue
            main.append(val.split(';')[0].replace(')', '').replace('(', '').strip(','))



    for index,i in enumerate(k):
        p = i.find_all("div",{"class":"listbox"})
        m = 0;
        for j in p:
            tem_var =[]
            v= (list(j.stripped_strings)[6:])
            stopwords = "* Available to members only"
            new_words = [word for word in v if word not in stopwords]
            
            stopwords = "Self-Serve Lobby Coin Machine"
            new_words1 = [word for word in new_words if word not in stopwords]

            stopwords ="Fax:"
            new_words2 = [word for word in new_words1 if word not in stopwords]

    
            patt = re.compile(r'[0-9-\(\) ]+$')
            hours= (" ".join(new_words2[3:]).replace("Duluth, MN 55816","").replace("Coin Machine Available",""))
            if patt.match(new_words2[0]):
                del new_words2[0]

            # hours = (" ".join(new_words2).replace("Coin Machine Available",""))
            phone =list(j.stripped_strings)[5]
            zipcode = list(j.stripped_strings)[3].split(',')[1].split( )[1]
            state = list(j.stripped_strings)[3].split(',')[1].split( )[0]
            city = list(j.stripped_strings)[3].split(',')[0]
            street_address = list(j.stripped_strings)[2]
            store_name.append(list(j.stripped_strings)[1])


            latitude = main[m].split(',')[0]
            longitute = main[m].split(',')[1]
            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state.strip())
            tem_var.append(zipcode.strip())
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("bank")
            tem_var.append(latitude)
            tem_var.append(longitute)
            tem_var.append(hours)
            tem_var.append(base_url)
           
            store_detail.append(tem_var)
            m+=1


   
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.membersccu.org")
        store.append(store_name[i])
        store.extend(store_detail[i])
     
        return_main_object.append(store) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
