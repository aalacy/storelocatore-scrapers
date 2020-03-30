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
  
    base_url= "https://www.traviniaitaliankitchen.com"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
  
    hours = []
    name_store=[]
    store_detail=[]
    phone=[]
    return_main_object=[]
    k=soup.find_all("div",{"id":"p7PM3_1"})


    for i  in k:
        a=(i.find_all('a'))
        for a1 in a[7:][:-8]:
            tem_var =[]
            base_url1= a1['href']
            r = session.get(base_url1)
            soup1= BeautifulSoup(r.text,"lxml")
            name = list(soup1.find_all("div",{"class":"box3content smaller"})[1].stripped_strings)[0]
            phone = list(soup1.find_all("div",{"class":"box3content smaller"})[1].stripped_strings)[1]
            

            v = list(soup1.find_all("div",{"class":"box3content smaller"})[1].stripped_strings)
      
            stopwords = "The Shops at Stonefield"
            new_words = [word for word in v if word not in stopwords]

            stopwords ='Village at Leesburg'
            new_words1 = [word for word in new_words if word not in stopwords]

            st = new_words1[2].replace("\n","").replace("           ","")
            city = new_words1[3].split(',')[0]
            state = new_words1[3].split(',')[1].split( )[0]
            zip1 = new_words1[3].split(',')[1].split( )[1]
            hours = (" ".join(new_words1[5:][:-1]).replace("VIEW OUR MENU Click to hear our Radio Spot 1",""))


            lat = soup1.find("iframe")['src'].split('2d')
            new_late = soup1.find("iframe")['src']
            kp = re.findall(r'[-+]?\d*\.\d+',new_late)
            lng = kp[1]
            if kp[0]=="99132.1996659177":
                del kp[0]

            if kp[0]=="-77.58972826832132":
                del kp[0]
            lat = (kp[0])
    
           
            tem_var.append("https://www.traviniaitaliankitchen.com")
            tem_var.append(name)

            tem_var.append(st)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zip1)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append(lat)
            tem_var.append(lng)
            tem_var.append(hours)
            tem_var.append(base_url1)
            print(tem_var)
            return_main_object.append(tem_var)
                            
  
 
    
    # for i in range(len(name_store)):
    #     store = list()
    #     store.append("https://theyard.com")
    #     store.append(name_store[i])
    #     store.extend(store_detail[i])
    #     return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()




