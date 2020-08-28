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
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    addresses = []
    return_main_object = []
    base_url = "https://www.fredericmalle.com"
    get_url = "https://www.fredericmalle.com/about#/stores/"
    r = session.get(get_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find_all("ul", {"class":"accordions accordions--countries js-accordion--countries"})[:17]
    for i in data:
        for j in i.find_all("div", {"class": "stores__location-info"}):
            state_name = i.find("div",{"class":"accordion_btn js-stores-country-name"}).text.strip().replace(" ",'-').replace(",",'').replace(".",'').lower().strip()
            
            location_name = j.find("div", {"class": "stores__location-name"}).text.strip()
            hour1 =j.find("div", {"class": "stores__location-hours"}).text.strip().replace("\n",'')

            if hour1 == '':
                hour = '<MISSING>'
            else:
                hour = hour1.replace("Please note, effective March 16, we have temporarily closed this boutique in line with government advisement.","<MISSING>").replace("Avenue is reopened, effective July 10.","").replace("Greenwich","").replace("Madison","")
                
            phone = j.find("div",{"class":"stores__location-phone"}).text.replace("TEL:",'').strip()
            
            if j.find("a") is not None:
                lat_tmp = j.find("a")['href']
                if len(lat_tmp.split("&sll=")) > 1:
                    latitude = lat_tmp.split("&sll=")[1].split("&")[0].split(",")[0]
                    longitude = lat_tmp.split("&sll=")[1].split("&")[0].split(",")[1]
                elif len(lat_tmp.split("/@")) > 1:
                    latitude = lat_tmp.split("/@")[1].split(",")[0]
                    longitude = lat_tmp.split("/@")[1].split(",")[1]
                else:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
        
            address_tmp = list(j.stripped_strings)
            if "NorthPark Center" in address_tmp:
                address = "NorthPark Center, 8687 North Central Expressway, Suite 400"
                city = "Dallas"
                state = "Texas"
                zip = "75225"
            elif (len(address_tmp)==5):
                address = address_tmp[1].rstrip(",")
                state_tmp1 = address_tmp[2]
                state_tmp2= BeautifulSoup(state_tmp1, "lxml").text#.replace("&nbsp","").split(',')
                ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(state_tmp2))
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(state_tmp2))
                if us_zip_list:
                    zip = us_zip_list[0]
                    country_code = "US"
                elif ca_zip_list:
                    zip = ca_zip_list[0]
                    country_code = "CA"    
                state_tmp3 = state_tmp2.replace(zip,'').split(',')
               
                try:
                    city = state_tmp3[-2].strip().replace("\xa0","")
                except:
                    city = state_tmp3[0].strip().replace("\xa0","")
                state = state_tmp3[-1].strip()
    
            elif (len(address_tmp)==6):
                if "Editions de Parfums Frederic Malle" in address_tmp:
                    address = address_tmp[1].rstrip(",")
                else:
                    address = address_tmp[-4].rstrip(",")

                if len(address_tmp[2].split(',')) == 2:
                    state_tmp = address_tmp[2].split(',')
                    city = state_tmp[0]
                    state_tmp1 = state_tmp[1].strip()
                    
                else:
                    state_tmp = address_tmp[3].split(',')
                    city = state_tmp[0]
                    state_tmp1= state_tmp[1].strip()
                 
                ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(state_tmp1))
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(state_tmp1))
            
                if us_zip_list:
                    zip = us_zip_list[0]
                    country_code = "US"
                elif ca_zip_list:
                    zip = ca_zip_list[0]
                    country_code = "CA"
                if state_tmp1.replace(zip,'').strip() == "Florida":
                    state = "FL"
                elif state_tmp1.replace(zip,'').strip() == "Texas":
                    state = "TX"
                    state = state_tmp1.replace(zip,'').strip()
            else:
                address = address_tmp[1].rstrip(",")
                state_tmp = address_tmp[2].split(',')
                city = state_tmp[0]
        
                try:
                    state_tmp1= state_tmp[1].strip()
                except:
                    state_tmp1= state_tmp[0]
               
                ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(state_tmp1))
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(state_tmp1))
            
                if us_zip_list:
                    zip = us_zip_list[0]
                    country_code = "US"
                elif ca_zip_list:
                    zip = ca_zip_list[0]
                    country_code = "CA"
                state = state_tmp1.replace(zip,'').strip()

            if "Editions de Parfums Frederic Malle" in location_name:
                page_url = "https://www.fredericmalle.com/about#/stores/"+str(state_name)+"/editions-de-parfums-frederic-malle"
            else:
                page_url = "https://www.fredericmalle.com/about#/stores/"+str(state_name)+"/stockists"

            if page_url == "https://www.fredericmalle.com/about#/stores/california/stockists":
                state = "CA"


            tem_var =[]
            tem_var.append(base_url)
            tem_var.append(location_name)
            tem_var.append(address)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zip)
            tem_var.append(country_code)
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append(latitude)
            tem_var.append(longitude)
            tem_var.append(hour)
            tem_var.append("<MISSING>")
            tem_var = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in tem_var]
            yield tem_var

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
