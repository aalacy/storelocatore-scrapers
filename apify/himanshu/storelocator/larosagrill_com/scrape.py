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
    base_url1= "https://www.larosagrill.com/wp-admin/admin-ajax.php?action=store_search&lat=40.712775&lng=-74.00597299999998&max_results=25&search_radius=50&autoload=1"
    r1 = session.get(base_url1)
    soup2= BeautifulSoup(r1.text,"lxml")

    base_url= "https://www.larosagrill.com/menu-locations/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    dec={}
    data = json.loads(str(soup).split('"address":')[1].split("],")[0]+"]")
    
    for  d in soup.find_all("div",{"class":re.compile("et_pb_section et_pb_section_")}):
        try:
            if "#" in d.find("h2").find("a")['href']:
                continue
            ids = d['id']
            page_ur=d.find("h2").find("a")['href']
            r3 = session.get(page_ur.replace("#",''))
            soup3= BeautifulSoup(r3.text,"lxml")
            lat = (soup3.find("div",{"class":"et_pb_map"})['data-center-lat'])
            log = (soup3.find("div",{"class":"et_pb_map"})['data-center-lng'])
            name = (soup3.find("div",{"class":"et_pb_column_7"}).find("h2").text.strip())
            phone = soup3.find("a",{"href":re.compile("tel")}).text.strip()
            st=list(soup3.find("div",{"class":re.compile("loction")}).stripped_strings)
            
            phone = st[-3]
            city=st[-5].split(",")[0]
            state = st[-5].split(",")[1].strip().split( )[0]
            zipp = st[-5].split(",")[1].strip().split( )[1]
            try:
                hours = list(soup3.find("h4",text=re.compile(" Store Hours")).parent.stripped_strings)[1]
            except:
                hours="<MISSING>"
            street_address = " ".join(st[:-5])
            tem_var=[]
            tem_var.append("https://www.larosagrill.com")

            tem_var.append(name)
            tem_var.append(street_address.replace(",",''))
            tem_var.append(city)
            tem_var.append(state.strip())
            tem_var.append(zipp.strip())
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append(lat)
            tem_var.append(log)
            tem_var.append(hours)
            tem_var.append(page_ur)
            # print("tem_var",tem_var)
            yield tem_var
           
        except:
            pass


    
def scrape():
    data = fetch_data()
    write_output(data)


scrape()


