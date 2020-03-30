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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    return_main_object=[]

    for i in range(1,3):
        base_url= "https://crenospizzaco.com/find-a-store/page/"+str(i)+"/?dest=Columbus%2C%20OH%2C%20United%20States&lat=39.9611755&long=-82.99879420000002"
        r = session.get(base_url,headers=headers)
        soup= BeautifulSoup(r.text,"lxml")

        k = soup.find_all("ul",{"class":"content"})
        lat1 = []
        log1 =[]
        for i in k:
            name = i.find_all("div",{"class":"list_box general"})
            lat=(i.find_all("script",{"type":"text/javascript"}))

            for l in lat:
                lat1.append(l.text.split("Creno")[0].split("new Array(")[-1].split(',')[0].replace("'",""))
                log1.append(l.text.split("Creno")[0].split("new Array(")[-1].split(',')[1].replace("'",""))
                
            for index,n in enumerate(name):
                tem_var=[]
                
                name = list(n.stripped_strings)[0]
                st = list(n.stripped_strings)[1].split(',')[0]
                city = list(n.stripped_strings)[1].split(',')[1].split('O')[0]

                zip1=(list(n.stripped_strings)[2].replace("Zip: ",""))
                phone = list(n.stripped_strings)[6]
                if len(" ".join(list(n.stripped_strings)[1].split(',')[2:]).replace(" United States","")) !=0:
                    state = (" ".join(list(n.stripped_strings)[1].split(',')[2:]).replace(" United States",""))
                else:
                    state = (list(n.stripped_strings)[1].split(',')[1].split( )[-1])

    
                tem_var.append("https://crenospizzaco.com")
                tem_var.append(name)
                tem_var.append(st)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zip1)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("crenospizzaco")
                tem_var.append(lat1[index])
                tem_var.append(log1[index])
                tem_var.append("<MISSING>")
                return_main_object.append(tem_var)
    
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


