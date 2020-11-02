import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast


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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url= "https://www.mdvnf.com/Locations.aspx"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    
    data = soup.find_all("div",{"class":"hentry","data-sync":"textbox_content"})
    store_name=[]
    store_detail=[]
    return_main_object=[]
    return_main_object1=[]
    address=[]
    k = soup.find_all("table",{"cellpadding":"4"})

    
    for i in k:
        k1 = i.find_all("td")
        for j in k1:
            tem_var=[]
            city = list(j.stripped_strings)[-1].split(',')[0]
            state = list(j.stripped_strings)[-1].split(',')[1].split( )[0]
            zip1 = list(j.stripped_strings)[-1].split(',')[1].split( )[1]
            name = list(j.stripped_strings)[:-2][0]
            st = " ".join(list(j.stripped_strings)[:-1][1:])

            
            if zip1 ==6 or zip1==7:
                contry ="CA"
            else:
                contry="US"

            store_name.append(name)
            tem_var.append(st)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zip1)
            tem_var.append(contry)
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("spartannash")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            store_detail.append(tem_var) 
    
            r = session.get("https://www.mdvnf.com/"+j.a['href'],headers=headers)
            soup1= BeautifulSoup(r.text,"lxml")
            k2 = soup1.find_all("table",{"cellspacing":"5"})

            for j in k2:
                v = j.find_all("td")
                for j in v:
                    tem_var=[]
                    p1 = list(j.stripped_strings)
                    if len(p1)==3:
                        city = p1[-1].split(',')[0]
                        zip1= p1[-1].split(',')[-1].split( )[-1]
                        state= p1[-1].split(',')[-1].split( )[0]
                        st = p1[1]
                        name = p1[0]

                        if zip1 ==6 or zip1==7:
                            contry ="CA"
                        else:
                            contry="US"

                        store_name.append(name)
                        tem_var.append(st)
                        tem_var.append(city)
                        tem_var.append(state)
                        tem_var.append(zip1)
                        tem_var.append(contry)
                        tem_var.append("<MISSING>")
                        tem_var.append("<MISSING>")
                        tem_var.append("spartannash")
                        tem_var.append("<MISSING>")
                        tem_var.append("<MISSING>")
                        tem_var.append("<MISSING>")
                        store_detail.append(tem_var) 
                    else:
                   

                        if p1[2][0:3]=='For':
                            del p1[2]
                        
                        city = p1[-1].split(',')[0]
                        state = p1[-1].split(',')[1:][-1].split( )[0]
                        zip1 = p1[-1].split(',')[1:][-1].split( )[1]
                        name = p1[0]

                        if city in " ".join(p1[1:3]):
                            del p1[1:3][-1]
                        
                        st= (" ".join(p1[1:3]).replace("Fort Smith, AR  72905","").replace("Little Rock, AR  72199","").replace("Homestead, FL  33039","").replace("Us Air Force","").replace("U.S. Army","").replace("U S Army","").replace("Homestead, FL  33039","").replace("Austin, TX  78703","").replace("Houston, TX  77034",""))


                        if zip1 ==6 or zip1==7:
                            contry ="CA"
                        else:
                            contry="US"

                
                        store_name.append(name)
                        tem_var.append(st.replace("Afs","").replace("St","").replace("AFB",""))
                        tem_var.append(city)
                        tem_var.append(state)
                        tem_var.append(zip1)
                        tem_var.append(contry)
                        tem_var.append("<MISSING>")
                        tem_var.append("<MISSING>")
                        tem_var.append("spartannash")
                        tem_var.append("<MISSING>")
                        tem_var.append("<MISSING>")
                        tem_var.append("<MISSING>")
                        store_detail.append(tem_var) 

          
            
       
    for i in range(len(store_name)):
        store = list()
        store.append("http://spartannash.com")
        store.append(store_name[i])
        store.extend(store_detail[i])

        if store[3] in address:
            continue
        
        address.append(store[3])

        return_main_object.append(store) 

    


    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


