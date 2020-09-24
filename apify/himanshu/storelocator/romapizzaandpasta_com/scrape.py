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
    base_url= "https://romapizzaandpasta.com/locations/"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    hours1=[]
    page_url = []
  
    k1  = soup.find_all("div",{"class":"x-column x-sm vc x-1-1"})
    for i in k1:
        names = i.find_all("strong")
        a = i.find_all("a")
        span = i.find_all("span")
        for s in span:
            hours1.append(" ".join(list(s.stripped_strings)))

        for a1 in a[:-1]:
            if "https:" in a1['href']:

                page_url.append(a1['href'])
                r = session.get(a1['href'],headers=headers)
                soup1= BeautifulSoup(r.text,"lxml")
                k = soup1.find_all("div",{"class":"col-lg-3"})
                for i in k:
                    hours = ''
                    tem_var =[]
                    p = i.find("div",{"class":"card-body"})
            
                    zipcode = list(p.stripped_strings)[2].split(',')[1].split( )[1]
                    state = list(p.stripped_strings)[2].split(',')[1].split( )[0]
                    city = list(p.stripped_strings)[2].split(',')[0]
                    street_address = list(p.stripped_strings)[1]
                    time =  p.find_all("div",{"class":"mt-2"})
                    phone = list(time[-1].stripped_strings)[-1]
                   
                    if len(list(time[-2].stripped_strings)) ==2:
                        hours = (list(time[-2].stripped_strings)[-1])
                    else:
                        hours ="<MISSING>"
                
                    tem_var.append(street_address)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zipcode)
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("romapizzaandpasta")
                    tem_var.append("<MISSING>")
                    tem_var.append("<MISSING>")
                    
                    store_detail.append(tem_var)

        for name in names[:-1]:
            store_name.append(name.text.replace("\n",""))

    del store_name[3]
    del page_url[3]


    arr=["https://www.opendining.net/menu/5bcf1d1b505ee9035f2a106d"]
    for arr1 in arr:
        page_url.append(arr1)
        tem_var=[]
        r = session.get(arr1,headers=headers)
        soup2= BeautifulSoup(r.text,"lxml")
        v2=list(soup2.find("div",{"class":"restaurant-info"}).stripped_strings)
       
        name = v2[0]
        
        addr = v2[1].split(",")

        st=addr[0]
        city = addr[1].replace("\n\t\t\t\t\t\t\t","")
        state = addr[2].strip().split(" ")[0]
        zip1 = addr[2].strip().split(" ")[1]
        phone = v2[2].strip()
        store_name.append(name)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("romapizzaandpasta")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        store_detail.append(tem_var)

    for i in range(len(store_name)):
        store = list()
        store.append("https://romapizzaandpasta.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append(hours1[i])
        store.append(page_url[i])
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        return_main_object.append(store) 

    return return_main_object
    


def scrape():
    data = fetch_data()
    write_output(data)
scrape()


