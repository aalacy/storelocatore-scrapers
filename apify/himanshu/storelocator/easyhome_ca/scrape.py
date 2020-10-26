import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('easyhome_ca')



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
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
        return str(hour) + ":" + k1 + " " + am

def fetch_data():
  
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url= "https://easyhome.ca/store/all"
    r = session.get(base_url,headers=headers,verify=False)
    soup= BeautifulSoup(r.text,"lxml")
  
    name_store=[]
    store_detail=[]
    
    return_main_object=[]
   
    k=json.loads(soup.text,strict=False)
    for index,i in enumerate(k):
        tem_var=[]
        st = i['address1']
        country = "CA"
        lat = i['latitude']
        log =i['longitude']
        postal =i['zip'].upper()
        name = i['storeName']
        storeCode = i['storeCode']
        state =i['state'].split('-')[0]
        city =i['city']
        phone =i["phone"]
        if "saturdayClose" in i or "saturdayOpen" in i:
            if  i['saturdayOpen']!= None:
                
                index = 2
                char = ':'
                saturdayOpen = i['saturdayOpen'][:index] + char + i['saturdayOpen'][index + 1:]+''+str(0)
                # logger.info(i['saturdayClose'])

                index1 = 2
                char = ':'
                saturdayClose = i['saturdayClose'][:index1] + char + i['saturdayClose'][index1 + 1:]+''+str(0)

                index2 = 2
                char = ':'
                weekdayOpen = i['weekdayOpen'][:index2] + char + i['weekdayOpen'][index2 + 1:]+''+str(0)
                # logger.info(weekdayOpen)

                index3 = 2
                char = ':'
                weekdayClose = i['weekdayClose'][:index3] + char + i['weekdayClose'][index3 + 1:]+''+str(0)

                # logger.info(weekdayClose)

                # time ="saturdayOpen" + ' '+saturdayOpen.replace("90:0","09:00")+ ' '+ 'saturdayClose'+ ' '+str(saturdayClose)+ ' '+'Mon-Fri'+' '+str(weekdayOpen)+' - '+ str(weekdayClose)
                time ='Mon-Fri:'+' '+str(weekdayOpen)+' - '+ str(weekdayClose)+ ', Sat: '+  saturdayOpen.replace("90:0","09:00")+' - ' + str(saturdayClose)
            
            else:
                time="<MISSING>"
                
            
            # logger.info(time.replace("saturdayOpen None saturdayClose None weekdayOpen None weekdayClose None","<MISSING>"))
        
        # else:
        #     time="<MISSING>"
            

        # logger.info(time)
       

       
 

        tem_var.append("https://easyhome.ca")
        tem_var.append(base_url)
        tem_var.append(name)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(postal)
        tem_var.append("CA")
        tem_var.append(storeCode)
        tem_var.append(phone)
        tem_var.append("easyhome")
        tem_var.append(lat)
        tem_var.append(log)
        tem_var.append(time.replace("saturdayOpen None saturdayClose None weekdayOpen None weekdayClose None","<MISSING>"))
        return_main_object.append(tem_var)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()




