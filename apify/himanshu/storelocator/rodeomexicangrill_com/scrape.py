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
    base_url= "https://www.rodeomexicangrill.com/"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"html5lib")
    return_main_object=[]
    lat = []
    lng =[]
    loc=(soup.find_all("div",{"class":"col-md-4 col-xs-12"}))
    k=soup.find("script",{"type":"application/json","class":"js-react-on-rails-component"})
    jd = json.loads(k.text)['preloadQueries'][0]['data']['restaurant']['locations']
    for data in jd:
        if data['lat']:
            lat.append(data['lat'])
            lng.append(data['lng'])
    for index,i in enumerate(loc):
        tem_var=[]
        name = list(i.stripped_strings)[0]
        st = " ".join(list(i.stripped_strings)[1:4])
        hours=" ".join(list(i.stripped_strings)[7:])
        city = list(i.stripped_strings)[4].split(',')[0]
        state = list(i.stripped_strings)[4].split(',')[1].split( )[0]
        zip1=list(i.stripped_strings)[4].split(',')[1].split( )[1]
        phone =list(i.stripped_strings)[6]
        hours = " ".join(list(i.stripped_strings)[7:])
        tem_var.append("https://www.rodeomexicangrill.com")
        tem_var.append(name)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("Restaurant")
        tem_var.append(lat[index])
        tem_var.append(lng[index])
        tem_var.append(hours)
        tem_var.append("<MISSING>")
        return_main_object.append(tem_var)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()





