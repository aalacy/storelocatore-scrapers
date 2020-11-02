import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
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
        return str(hour) + ":" + str(int(str(time / 60).split(".")[1]) * 6) + " " + am


def fetch_data():
   

    return_main_object = []
    addresses = []
    headers = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    "Accept":"*/*",
    }
    base_url= "https://www.iamaflowerchild.com/api/?action=get-all-locations"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    k =(json.loads(soup.text))
    for i in k['data']:
        r1 = session.get(i['permalink'],headers=headers)
        soup1= BeautifulSoup(r1.text,"lxml")
       
        if "statusIndicationMessageFriendly" in i['location'] and  i['location']['statusIndicationMessageFriendly'] == "Opening Soon": 
            pass
        else:
            tem_var =[]
            if  "displayNameSimplified" in  i['location']:
                name = i['location']['displayNameSimplified']
      
            if "address"in i['location']:
                st = i['location']['address']
            else:
                st = "<MISSING>"
            
            city = i['location']['city']
            state = i['location']['state']
            if "zip" in i['location']:
                zip1 = i['location']['zip']
            else:
                zip1 = "<MISSING>"

            if "phone" in i['location']:
                phone = i['location']['phone']
            else:
                phone = "<MISSING>"
           
            r1 = session.get(i['permalink'],headers=headers)
            soup1= BeautifulSoup(r1.text,"lxml")
            json1 = json.loads(soup1.find("script",{'type':"application/ld+json"}).text)
            lat = json1['geo']['latitude']
            lng = json1['geo']['longitude']          
            time1 = soup1.find("ul",{"class":"location-hours"}).text.strip().replace("\n","").replace('Daily','Daily ')            
            tem_var.append("https://www.iamaflowerchild.com")
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
            tem_var.append(time1 if time1 else "<MISSING>")
            tem_var.append(i['permalink'])           
            if tem_var[2] in addresses:
                continue
            addresses.append(tem_var[2])
        
            return_main_object.append(tem_var)


    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
