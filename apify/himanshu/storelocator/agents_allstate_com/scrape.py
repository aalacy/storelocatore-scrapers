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

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept':"application/json"

    }

    # it will used in store data.
 
    for zip_code in zips:
        # data = '{"strLocation":"85029","strLat":33.5973469,"strLng":-112.10725279999997,"strRadius":"100","country":"US"}'
        # print("zips === " + str(zip_code))
        try:
            r = requests.get('https://agents.allstate.com/locator.html?search='+str(zip_code)+'&r=1000',headers=headers)
            soup1= BeautifulSoup(r.text,"lxml").text
            address=[]
        
            k = json.loads(soup1)
            for i in k['response']['entities']:
                tem_var=[]
                postalCode = i['profile']['address']['postalCode']
                state = i['profile']['address']['region']
                city= i['profile']['address']['city']
                time=''
                if i['profile']['address']['line2']==None:
                    st=''
                else:
                    st = i['profile']['address']['line2']
                st=  i['profile']['address']['line1'] + ' '+time
                if "facebookCallToAction" in i['profile']:
                    phone =(i['profile']['facebookCallToAction']['value'])
                else:
                    phone = "<MISSING>"


                if "hours" in i['profile']:
                    for j in i['profile']['hours']['normalHours']:
                        
                        if j['intervals'] !=[]:
                            start =j['intervals'][0]['start']
                            end= j['intervals'][0]['end']
                            start1 = minute_to_hours(start)
                            end1 = minute_to_hours(end)

                        
                            time = (j['day'] + ' ' +start1 +' '+end1)

                if "yextDisplayCoordinate" in i['profile']:
                    lat = i['profile']['yextDisplayCoordinate']['lat']
                    lon = i['profile']['yextDisplayCoordinate']['long']
                else:
                    lat = "<MISSING>"
                    lon = "<MISSING>"

                name  = i['profile']['name']
                # print(i['profile']['name'])
                # exit()
                tem_var.append("https://agents.allstate.com")
                tem_var.append(name if name  else "<MISSING>")
                tem_var.append(st if st else "<MISSING>")
                tem_var.append(city if city else "<MISSING>")
                tem_var.append(state if state else "<MISSING>" )
                tem_var.append(postalCode if postalCode else "<MISSING>")
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone if phone else "<MISSING>" )
                tem_var.append("agents.allstate")
                tem_var.append(lat if lat else "<MISSING>" )
                tem_var.append(lon if lon else  "<MISSING>")
                tem_var.append(time if time else "<MISSING>")
                if tem_var[3] in addresses:
                    continue
            
                addresses.append(tem_var[3])
                # print(tem_var)
                yield tem_var
        except:
            continue

               

           

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
