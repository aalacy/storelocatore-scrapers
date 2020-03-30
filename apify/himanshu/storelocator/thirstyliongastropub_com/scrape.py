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
    base_url= "https://www.thirstyliongastropub.com/texas"
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"
    }
    
    arr=['arizona','colorado',"oregon",'texas']
    mapLat =[]
    mapLng =[]
    store_name=[]
    store_detail=[]
    return_main_object=[]
    hours1 =[]
    for p in arr:
        base_url= "https://www.thirstyliongastropub.com/"+str(p)
        r = session.get(base_url)
        soup= BeautifulSoup(r.text,"lxml")
        new_name = str(p)
        k=(soup.find_all("div",{"class":"sqs-block html-block sqs-block-html"}))
        lat = (soup.find_all("div",{"class":"sqs-block map-block sqs-block-map"}))
        for i in lat:
            json1 = json.loads(i.attrs['data-block-json'])
            mapLat.append(json1['location']['mapLat'])
            mapLng.append(json1['location']['mapLng'])



        # print("================",str(p))
        for i in k:
            
            p = i.find_all("p")
            for p1 in p:
                if "ADDRESS" in p1.text:
                    tem_var=[]

                    if len(list(i.stripped_strings)) ==10  or len(list(i.stripped_strings))==7:
                        phone =''
                        state = list(i.stripped_strings)[1].split('|')[-1].split(',')[-1].split( )[0]
                        zip1 = list(i.stripped_strings)[1].split('|')[-1].split(',')[-1].split( )[1]
                        city = list(i.stripped_strings)[1].split('|')[-1].split(',')[-2].replace("Grandscape - ","")
                        city =(city.strip().split('\xa0')[-1])
                        st =(list(i.stripped_strings)[1].split('|')[0].replace(", TX 75056",""))
                        if "PHONE:" in list(i.stripped_strings):
                            phone = (list(i.stripped_strings)[8])
                        else:
                            phone = "<MISSING>"

                        hours=(" ".join(list(i.stripped_strings)[3:][:7]).replace("PHONE: 817.283.9000 Free Valet Parking on Friday & Saturday Nights",""))
                        store_name.append(new_name.encode('ascii', 'ignore').decode('ascii').strip())
                        tem_var.append(st.encode('ascii', 'ignore').decode('ascii').strip())
                        tem_var.append(city.encode('ascii', 'ignore').decode('ascii').strip())
                        tem_var.append(state.encode('ascii', 'ignore').decode('ascii').strip())
                        tem_var.append(zip1.encode('ascii', 'ignore').decode('ascii').strip())
                        tem_var.append("US")
                        tem_var.append("<MISSING>")
                        tem_var.append(phone.replace("TBD","<MISSING>"))
                        tem_var.append("thirstyliongastropub")
                      
                        hours1.append(hours)
                        store_detail.append(tem_var)
                    else:
                        st = list(i.stripped_strings)[1].split("\xa0")[0].replace("|","").split(",")[0]
                        city = list(i.stripped_strings)[1].split("|")[1].split(',')[0]
                        state = list(i.stripped_strings)[1].split("|")[1].split(',')[1].split( )[0]
                        zip1 = list(i.stripped_strings)[1].split("|")[1].split(',')[1].split( )[1]
                        phone = list(i.stripped_strings)[-1]
                        hours = " ".join(list(i.stripped_strings)[3:][:-2])
                        
              
                        store_name.append(new_name.encode('ascii', 'ignore').decode('ascii').strip())
                        tem_var.append(st.encode('ascii', 'ignore').decode('ascii').strip())
                        tem_var.append(city.encode('ascii', 'ignore').decode('ascii').strip())
                        tem_var.append(state.encode('ascii', 'ignore').decode('ascii').strip())
                        tem_var.append(zip1.encode('ascii', 'ignore').decode('ascii').strip())
                        tem_var.append("US")
                        tem_var.append("<MISSING>")
                        tem_var.append(phone.replace("TBD","<MISSING>"))
                        tem_var.append("<MISSING>")

                        hours1.append(hours)
                        store_detail.append(tem_var)
                    
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.thirstyliongastropub.com")
        store.append(store_name[i].encode('ascii', 'ignore').decode('ascii').strip())
        store.extend(store_detail[i])
        store.append(mapLat[i])
        store.append(mapLng[i])
        store.append(hours1[i].encode('ascii', 'ignore').decode('ascii').strip())
        # store.append(url[i])
        if  "3077 W. Frye Rd  Chandler" in store or "21001 North Tatum" in store or "Grandscape -The Colony" in store or "15900 La Cantera Pkwy" in store:
            pass
        else: 
            return_main_object.append(store) 
    
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


