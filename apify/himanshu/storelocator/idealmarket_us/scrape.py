import csv
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup as bs
import re
import json
from sgrequests import SgRequests

s = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',newline='') as output_file:
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
    base_url= "http://idealmarket.us/store-locator/"
    r = s.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    for dt in soup.find("div",{"class":"mpfy-mll-list"}).find_all("div",{"class":re.compile("mpfy-mll-location")}):
        val = dt.find("a",text=re.compile("More Details"))['data-mpfy-value']

        url = "http://idealmarket.us/map-location/"+list(dt.stripped_strings)[0].replace(" #",'-').replace(" ",'-').lower()+"/?mpfy_map="+str(val)

        
        headers = {
        'Accept': 'text/html, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9,pt;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'idealmarket.us',
        'Referer': 'http://idealmarket.us/map-location/ideal-market-1/?mpfy_map='+str(val)+'&mpfy-pin='+str(val),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        }

        response = bs(s.get(url,headers=headers).text,'lxml')
        try:
            phone=(list(response.find("div",{"class":"mpfy-p-entry"}).stripped_strings)[-1].replace("USA","<MISSING>"))
        except:
            phone="270-442-4387"

        store_number = list(dt.stripped_strings)[0].split("#")[-1]
        name = list(dt.stripped_strings)[0].split("#")[0]
        adrr = list(dt.stripped_strings)
        if "Ideal Market" in adrr:
            del adrr[0]
            del adrr[0]
        if adrr[0] == "Subway":
            del adrr[0]
        if adrr[0] == "Ideal Market":
            del adrr[0]
        street_address = (adrr[0].split("|")[0])
        city = adrr[0].split("|")[1].split(",")[0]
        state = adrr[0].split("|")[1].split(",")[1]
        zipcode = adrr[0].split("|")[1].split(",")[2]
        latitude = dt.find("a",{"href":re.compile("http://www.google.com")})['href'].split("daddr=")[1].split(",")[0]
        longitude = dt.find("a",{"href":re.compile("http://www.google.com")})['href'].split("daddr=")[1].split(",")[1]
 
        tem_var =[]
        tem_var.append("http://idealmarket.us/")
        tem_var.append(name)
        tem_var.append(street_address)
        tem_var.append(city)
        tem_var.append(state.strip())
        tem_var.append(zipcode.strip())
        tem_var.append("US")
        tem_var.append(store_number)
        tem_var.append(phone if phone else "<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(latitude)
        tem_var.append(longitude)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")

        yield tem_var
    
  
def scrape():
    data = fetch_data()
    write_output(data)


scrape()


