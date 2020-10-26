import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mightytaco_com')





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

    base_url= "https://www.mightytaco.com/Locations"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    hours =[]
    phone=[]
    lat =[]
    lng =[]
    mark1 =[]
    mark2 =[]
    script = soup.find_all("script")
    mark = soup.find_all("div",{'class':"locationItem"})
    for i in mark:
        # logger.info(i.attrs['id'])
        mark1.append(i.attrs['id'])

    for i in script:
        
        if "Initiate Google Maps" in i.text:
            p = (i.text.split("GMap.init(")[1].split("',")[0].replace("{","").split('Marker_'))
            
           
            for index,i in enumerate(p):
                # for j in mark1:
              
                if 'json:' in i.split('"Groups"'):
                    pass
                else:
                    v = i.split("}")[0].split(":")[1].split(',')[0]
                    
                    if "Groups"  in  v:
                        pass
                    else:
                        # logger.info(i.split("}")[0])
                        mark2.append(i.split("}")[0])
   
    k=(soup.find_all("div",{'class':'address'}))
    k1=(soup.find_all("div",{'class':'hours'}))
    k2=(soup.find_all("div",{'class':'phoneRow clear'}))
    
    for index,j in enumerate(mark1):
        id1 = j.split("_")[1]
        
        id2 = mark2[index].split(",")[0].replace('"',"")
        for index,i in enumerate(range(len(mark2))):
           
        #    logger.info(index)
           
           if id1 == mark2[i].split(",")[0].replace('"',""):
                # logger.info(mark2[i].split(",")[2].replace('"',"").replace("longitude:",""))
                lat.append(mark2[i].split(",")[1].replace('"',"").replace("latitude:",""))
                lng.append(mark2[i].split(",")[2].replace('"',"").replace("longitude:",""))
                # logger.info(mark2[index].split(",")[2].replace('"',"").replace("longitude:",""))
            
                

        
        # logger.info(mark2[index].split(",")[0].replace('"',""))
  
    for j in k2:
        phone.append(list(j.stripped_strings)[0])
       
    for j in k1:
        hours.append(" ".join(list(j.stripped_strings)))
        
    # logger.info(lat)
    for index,j in enumerate(k,start=0):
        
        tem_var=[]
        # logger.info(index)
        st =(list(j.stripped_strings)[0].split(',')[0])
        city = list(j.stripped_strings)[0].split(',')[1]
        state = list(j.stripped_strings)[0].split(',')[2].split( )[0]
        zip1 = list(j.stripped_strings)[0].split(',')[2].split( )[1]
       
        tem_var.append("https://www.mightytaco.com")
        tem_var.append(city)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone[index])
        tem_var.append("<MISSING>")
        tem_var.append(lat[index])
        tem_var.append(lng[index])
        tem_var.append(hours[index].replace(")"," ").replace("("," "))
        tem_var.append(base_url)
        return_main_object.append(tem_var)
   
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


