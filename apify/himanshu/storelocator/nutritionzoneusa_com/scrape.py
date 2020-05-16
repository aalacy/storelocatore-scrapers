import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    locator_domain = "https://www.nutritionzoneusa.com"
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
    }
    r= session.get("https://cdn.shopify.com/s/files/1/0254/4114/0816/t/3/assets/sca.storelocator_scripttag.js?75&shop=nutritionzoneshop.myshopify.com")
    script = json.loads(r.text.split('"locationsRaw":"')[1].split('"};')[0].replace("\\",""))
    for i in script:
        # print(i)
        store_number = i["id"]
        location_name = i["name"]
        if "address2" in script:
            street_address = i["address"]+ " "+ i["address2"]
        else:
            street_address = i["address"]
        city = i["city"]
        state = i["state"]
        try:
            zipp = i["postal"]
        except:
            #print(i)
            zipp = "<MISSING>"
        latitude = i["lat"]
        longitude = i["lng"]
        country_code = "US"
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        page_url = "https://www.nutritionzoneusa.com/pages/store-locator"
        location_type = "<MISSING>"
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = [str(x).encode('ascii','ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

        #print("data = " + str(store))
        #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        yield store

  

    # r = session.get(base_url)
    # main_soup= BeautifulSoup(r.text,"lxml")
    # return_main_object =[]
    # store_detail =[]
    # store_name=[]
    # k  = main_soup.find_all("div",{"class":"col sqs-col-6 span-6"})
    # for i in k:
    #     # print(i.find_all('p'))
    #     for j in i.find_all('h3'):
    #         if list(j.stripped_strings)  != []:
    #             if list(j.stripped_strings)[0] == ".":
    #                 pass
    #             else:
    #                 store_name.append(list(j.stripped_strings)[0])
    #     for index,j in enumerate(i.find_all('p')):
    #         tem_var=[]
    #         if list(j.stripped_strings)  != []:
    #             if list(j.stripped_strings)[0] == ".":
    #                 pass
    #             else:
    #                 state = list(j.stripped_strings)[0].split(',')[-1].split( )[0]
    #                 # print(list(j.stripped_strings)[0])
    #                 zip1 = list(j.stripped_strings)[0].split(',')[-1].split( )[1]
    #                 city = list(j.stripped_strings)[0].split(',')[-2]
    #                 st = (" ".join(list(j.stripped_strings)[0].split(',')[:2]).replace("Charlotte","").replace("Raleigh","").replace("Santee","").replace("Sylmar","").replace("Lubbock",""))
    #                 # tem_var.append("https://www.nutritionzoneusa.com")
    #                 # tem_var.append(store_name[index])
    #                 tem_var.append(st.strip())
    #                 tem_var.append(city.strip())
    #                 tem_var.append(state)
    #                 tem_var.append(zip1)
    #                 tem_var.append("US")
    #                 tem_var.append("<MISSING>")
    #                 tem_var.append("<MISSING>")
    #                 tem_var.append("nutritionzoneusa")
    #                 tem_var.append("<MISSING>")
    #                 tem_var.append("<MISSING>")
    #                 tem_var.append("<MISSING>")
    #                 print(tem_var)
    #                 store_detail.append(tem_var)
    #                 # print(tem_var)
    #                 # return_main_object.append(tem_var) 


    # for i in range(len(store_name)):
    #    store = list()
    #    store.append("https://www.nutritionzoneusa.com")
    #    store.append(store_name[i])
    #    store.extend(store_detail[i])
    #    return_main_object.append(store) 
    #    yield return_main_object

    # return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
