import csv
import requests
from bs4 import BeautifulSoup
import re
import json


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
    base_url= "https://www.american1cu.org/locations"
    r = requests.get(base_url)
  
    soup= BeautifulSoup(r.text.replace('<div class="listbox" />','<div class="listbox" >'),"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    
    soup1 = soup.find_all("script",{"type":"text/javascript"})
    lat = []
    log = []
    st1 = []
    script =''
    # for i in soup1:
    #     if "var gmarkers" in i.text:
    #         script = i.text
            # h = i.text.split("new google.maps.LatLng(")
            # for index,j in enumerate(h):
                
            #     if len(h[index].split(")")[0].split("function initialize(")[0].split("var map = null;")) !=2:
            #         lat.append(h[index].split(")")[0].split("function initialize(")[0].split("var map = null;")[0].split(',')[0])
            #         log.append(h[index].split(")")[0].split("function initialize(")[0].split("var map = null;")[0].split(',')[1])
    
    
    
    k = soup.find_all("div",{"class":"listbox"})
    for index,i in enumerate(k):
 
        tem_var=[]
        if len(list(i.stripped_strings)) != 4:
            name = list(i.stripped_strings)[0]
            st = list(i.stripped_strings)[2]
            city = list(i.stripped_strings)[3].split(',')[0]
            state = list(i.stripped_strings)[3].split(',')[1].split( )[0]
            zip1 = list(i.stripped_strings)[3].split(',')[1].split( )[1]

            v= list(i.stripped_strings)
            if v[4]=="Phone:":
                del v[4]

            phone = v[4].replace("Lobby Hours:","<MISSING>").replace("Drive-Thru Hours:","<MISSING>")

            p = list(i.stripped_strings)

            if p[4]=="Phone:":
                del p[4]
                del p[4]
          
            if p[4]=="Fax:":
                del p[4]
                del p[4]

            if p[4]=="Phone Banking:":
                del p[4]
                del p[4]
        
            hours = (" ".join(p[4:7]).replace("This is not a public branch - DTE Employees and Retirees only.",""))
            location_type = "American 1 Credit Union Branches"

        else:

            name = list(i.stripped_strings)[0]
            st = list(i.stripped_strings)[2]
            city = list(i.stripped_strings)[3].split(',')[0]
            state = list(i.stripped_strings)[3].split(',')[1].split( )[0]
            zip1 = list(i.stripped_strings)[3].split(',')[1].split( )[1]
            hours = "<MISSING>"
            location_type = "American 1 Credit Union ATMs"

        st1.append(st)
        tem_var.append("https://www.american1cu.org")
        tem_var.append(name)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state.strip())
        tem_var.append(zip1.strip())
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append(location_type)
      

    # for i in soup1:
    #     if "var gmarkers" in i.text:
    #         for j in range(len(st1)):
    #             script = i.text
                
              
        # if index == 0:
        #     lat_long = soup.text.split('</b><br />930 W. North St.')[0].split('new google.maps.LatLng(')[1].split("),")[0]
        #     print(st)
        #     print(lat_long)
        # print("st == "+st)
        # print("lat_long == "+lat_long)
        
        
        tem_var.append("<INACCESSIBLE>")
        tem_var.append("<INACCESSIBLE>")
        tem_var.append(hours if hours else "<MISSING>" )
        return_main_object.append(tem_var)

    
    return return_main_object
   



def scrape():
    data = fetch_data()
    write_output(data)


scrape()


