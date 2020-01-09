import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()

def fetch_data():
    base_url= "https://www.choicehotels.com/cms/pages/comfort-suites/sitemap?d=DESKTOP&applocale=en-us&sitename=us"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    
    base = "https://www.choicehotels.com/comfort-suites/sitemap"
    r1 = session.get(base)
    soup1= BeautifulSoup(r1.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    addresses=[]
    phone =[]
    link = (soup.find_all("h6",{"class":"col-xs-6"}))
    for i in link:
        if i.a != None:
            r1 = session.get("https://www.choicehotels.com/cms/pages/choice-hotels/"+str(i.a['href'].split("/")[1])+"/comfort-suites?d=DESKTOP&applocale=en-us&sitename=us")
            soup1= BeautifulSoup(r1.text,"lxml")
            link2 = (soup1.find_all("a"))
            if link2 !=[]:
                for j in link2:
                    id1 =  j['href'].replace("/rates","").split('/')[-1]
                    if "hotels" in id1:
                        pass
                    else:
                        tem_var=[]
                        json_data = session.get("https://www.choicehotels.com/webapi/hotel/"+str(id1)+"?preferredLocaleCode=en-us&rooms=10&siteName=us").json()
                        
                        country = json_data['hotel']['address']['country'].strip()
                        if 'US' == country or 'CA' == country:
                            name = json_data['hotel']['name']
                            city = json_data['hotel']['address']['city']
                            st = json_data['hotel']['address']['line1']
                            if "postalCode" in json_data['hotel']['address']:
                                zip1 = json_data['hotel']['address']['postalCode']
                            else:
                                zip1 ="<MISSING>"
                            if "subdivision" in json_data['hotel']['address']:
                                state = json_data['hotel']['address']['subdivision']
                            else:
                                state = "<MISSING>"
                            phone = json_data['hotel']["phone"]
                            lat  =json_data['hotel']["lat"]
                            lon  =json_data['hotel']["lon"]

                            tem_var.append("https://www.choicehotels.com")
                            tem_var.append(name)
                            tem_var.append(st)
                            tem_var.append(city)
                            tem_var.append(state)
                            tem_var.append(zip1)
                            tem_var.append(country)
                            tem_var.append("<MISSING>")
                            tem_var.append(phone)
                            tem_var.append("<MISSING>")
                            tem_var.append(lat)
                            tem_var.append(lon)
                            tem_var.append("<MISSING>")
                            tem_var.append("https://www.choicehotels.com"+j['href'])
                            if tem_var[2] in addresses:
                                continue
                            addresses.append(tem_var[2])
                            yield tem_var
  
def scrape():
    data = fetch_data()
    write_output(data)


scrape()


