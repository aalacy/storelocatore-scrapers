import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def minute_to_hours(time):
    am = "AM"
    hour = int(time / 60)
    if hour > 12:
        am = "PM"
        hour = hour - 12
    if int(str(time / 60).split(".")[1]) == 0:
        
        return str(hour) + ":00" + " " + am
        
    else:
        k1 = str(int(str(time / 60).split(".")[1]) * 6)[:2]
        # print(k1[:2])
        # round(answer, 2)
        return str(hour) + ":" + k1 + " " + am
        


def fetch_data():
    zips = sgzip.for_radius(100)
    # zips =sgzip.coords_for_radius(50)
    return_main_object = []
    addresses = []
    store_detail=[]
    store_name=[]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',

    }

    for zip_code in zips:
        j =0
        while j!=-1:
            r = requests.get(
                'https://www.tumi.com/store-finder?q='+zip_code+'&searchRadius=100&page='+str(j),
                headers=headers)

            soup1= BeautifulSoup(r.text,"lxml")
            id1 = soup1.find("form",{"id":"myStoreForm"})
            soup2 =soup1.find_all("div",{"class":"span12"})
            if id1 == None:
                j=-1
            else:
                j=j+1
                for i in soup2:
                    k = i.find("div",{"class":"locator-storedetails"})
                    if k != None:
                        tem_var=[]
                        lng = k.find("div",{"class":"locator-storename"}).a['href'].split('lat=')[1].split("&long=")[1].split("&")[0]
                        lat =k.find("div",{"class":"locator-storename"}).a['href'].split('lat=')[1].split("&long=")[0]
                        name = k.find("div",{"class":"locator-storename"}).a.text.replace("\t","").replace("\n","").replace("\xa0-\xa0","")
                        st1 = list(k.find("div",{"class":"locator-address"}))
                        if len(st1)==10:
                            st = st1[0].replace('\t',"").replace("\n"," ")
                            state = st1[4].strip().split('-')[0]
                            phone = st1[7].text
                            city2=st1[2].replace('\t',"").replace("\n","").split(",")
                            if len(city2)==2:
                                city = city2[0].rstrip()
                                state = city2[1]
                            else:
                                city = city2[0].rstrip()
                                state = "<MISSING>"
                            zip1 = (st1[4].strip().split('-')[0])
                            # print(st1[2].replace('\t',"").replace("\n","").split(","))
                        else:
                            phone  = st1[-3].text
                            del st1[1]
                            st = " ".join(st1[:2])
                            city = st1[3].replace('\t',"").replace("\n","").strip().split(',')[0]
                            state= st1[3].replace('\t',"").replace("\n","").strip().split(',')[1]
                            zip1 = st1[5].strip().split('-')[0]
                            phone  = st1[8].text
                        time = k.find("ul",{"class":"locator-hours"})
                        if time != None:
                            time1 = " ".join(list(time.stripped_strings))
                        else:
                            time1 = "<MISSING>"

                        if len(zip1)==6 or len(zip1)==7:
                            c = "CA"
                        else:
                            c = "US"

                        # tem_var.append("https://www.tumi.com")
                        store_name.append(name if name  else "<MISSING>")
                        tem_var.append(st.replace('\t',"").replace("\n","") if st else "<MISSING>")
                        tem_var.append(city.lstrip().rstrip() if city else "<MISSING>")
                        tem_var.append(state if state else "<MISSING>" )
                        tem_var.append(zip1 if zip1 else "<MISSING>")
                        tem_var.append(c)
                        tem_var.append("<MISSING>")
                        tem_var.append(phone if phone else "<MISSING>" )
                        tem_var.append("tumi")
                        tem_var.append(lat if lat else "<MISSING>" )
                        tem_var.append(lng if lng else  "<MISSING>")
                        tem_var.append(time1 if time1 else "<MISSING>")
                        store_detail.append(tem_var)
                        # if tem_var[3] in address:
                        #     continue
                    
                        # address.append(tem_var[3])
                        
                      

    for i in range(len(store_name)):
       store = list()
       store.append("https://www.tumi.com")
       store.append(store_name[i])
       store.extend(store_detail[i])
       if store[3] in addresses:
           continue
                
       addresses.append(store[3])
    #    print(store)
       yield store

    # return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
