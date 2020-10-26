import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('napoleonsbakery_com')




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
    return_main_object = []
    addresses = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url = locator_domain= 'http://napoleonsbakery.com/'
    page_url= "http://napoleonsbakery.com/locations.php"
    r = session.get(page_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")

    for loc in soup.find('div',{'id':'location'}).find_all('div',{'id':'single'}):
        for p in loc.find_all('p',class_='bodytext'):
            ch = p.strong.text.split('-')
            state = "<MISSING>"

            city = loc.h4.text.strip()
            location_name = city
            if len(ch) == 2:
                hours_of_operation = ch[-1].strip()
            else:
                hours_of_operation = "<MISSING>"
            zipp = "<MISSING>"
            country_code = "US"
            store_number = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            location_type = "<MISSING>"
            street_address = p.strong.nextSibling.nextSibling.strip()
            phone = list(p.stripped_strings)[-1].strip()
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
            store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            store = [x if x else "<MISSING>" for x in store]

            if store[2] in addresses:
                continue
            addresses.append(store[2])
            # logger.info(city,state)
            #logger.info("data = " + str(store))
            #logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            return_main_object.append(store)

    return return_main_object



    # data = soup.find_all("div",{"class":"hentry","data-sync":"textbox_content"})
    # store_name=[]
    # store_detail=[]
    # return_main_object=[]

    # k = (soup.find_all("div",{"id":"container"}))
    # s = []
    # for st in soup.find('div',{'id':'navgallery'}).find_all('li'):
    #     try:
    #         state_tag = st['data-scroll']
    #         state_list = st.text

    #     except:
    #         continue
    #     s.append(state_list)
    # logger.info(s)

    # for i in k:
    #     k1 = i.find_all("li")
    #     for j in k1:
    #         tem_var =[]
    #         tem_var1 = []
    #         data = list(j.stripped_strings)
    #         stopwords = "24 hours"
    #         new_words = [word for word in data if word not in stopwords]

    #         if len(new_words) != 1 and new_words !=[]:

    #             if "24 hours" in data[1]:
    #                 hours = (data[1])

    #             else:
    #                 if "Kailua*" in data[0]:
    #                     hours = "24 hours"
    #                 else:

    #                     hours = "<MISSING>"
    #             # logger.info(data[0])
    #             store_name.append(new_words[0])
    #             street_address = (new_words[1])
    #             # state = s.pop(0)
    #             # logger.info(state)

    #             phone = (new_words[2])



    #             tem_var.append(street_address.replace("*-","").replace("*","").replace("-","").replace("\u2011",""))

    #             tem_var.append(new_words[0].replace("*-","").replace("*","").replace("-","").replace("\u2011",""))
    #             tem_var.append("<MISSING>")
    #             tem_var.append("<MISSING>")
    #             tem_var.append("US")
    #             tem_var.append("<MISSING>")

    #             tem_var.append(phone.replace("\u2011",""))

    #             tem_var.append("napoleonsbakery")
    #             tem_var.append("<MISSING>")
    #             tem_var.append("<MISSING>")
    #             tem_var.append(hours)
    #             store_detail.append(tem_var)




    # for i in range(len(store_name)):
    #     store = list()
    #     store.append("http://napoleonsbakery.com")
    #     store.append(store_name[i].replace("-","").replace("*",""))
    #     store.extend(store_detail[i])
    #     # logger.info(store)
    #     return_main_object.append(store)

    # return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


