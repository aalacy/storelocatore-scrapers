import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip




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
    # zips = sgzip.for_radius(100)
    zips =sgzip.coords_for_radius(50)

   
 
    return_main_object = []
    addresses = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
   

    }

    # it will used in store data.
 
    for zip_code in zips:
        # data = '{"strLocation":"85029","strLat":33.5973469,"strLng":-112.10725279999997,"strRadius":"100","country":"US"}'
        # print("zips === " + str(zip_code))
        try:
            r = session.get(
                'https://info3.regiscorp.com/salonservices/siteid/100/salons/searchGeo/map/'+zip_code[0]+'/'+zip_code[1]+'/0.8/0.8/true',
                headers=headers)
            soup1= BeautifulSoup(r.text,"lxml").text
            k = json.loads(soup1)
            for i in k['stores']:
                tem_var=[]
                st1 = i['subtitle']
                st = i['subtitle']
                name = i['title']
                phone = i['phonenumber']
                latitude = i['latitude']
                longitude = i['longitude']
                time  = ''
                if "store_hours" in i:
                    store_hours = i['store_hours']
                    
                
                    for j in store_hours:
                        time = time + ' ' +j['days']+ ' '+ j['hours']['open'] + ' '+ j['hours']['open']

                st = st1.split(',')[0]
                city = st1.split(',')[1]
                state = st1.split(',')[2].split( )[0]
                zip2 = st1.split(',')[2].split( )[1]

                if len(zip2)==3:
                    zip1 = "<MISSING>"
                else:
                    zip1 = zip2
                # city = st.split(',')[0]
                # state = st.split(',')[1].split( )[0]
                # zip1 = st.split(',')[1].split( )[1]
            
                tem_var.append("https://www.signaturestyle.com")
                tem_var.append(name if name  else "<MISSING>")
                tem_var.append(st if st else "<MISSING>")
                tem_var.append(city if city else "<MISSING>")
                tem_var.append(state if state else "<MISSING>" )
                tem_var.append(zip1 if zip1 else "<MISSING>")
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone if phone else "<MISSING>" )
                tem_var.append("signaturestyle")
                tem_var.append(latitude if latitude else "<MISSING>" )
                tem_var.append(longitude if longitude else  "<MISSING>")
                tem_var.append(time if time else "<MISSING>")
                print(tem_var)
                if tem_var[3] in addresses:
                    continue
                addresses.append(tem_var[3])
                return_main_object.append(tem_var)
        
        except:
            continue


    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
