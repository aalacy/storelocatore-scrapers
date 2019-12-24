import csv
import requests
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


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    addresses = []

    base_url = "https://www.fredericmalle.com"
    get_url = "https://www.fredericmalle.com/about#stores"
    r = requests.get(get_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    # print(soup)
    return_main_object = []
    main = soup.find_all("div", {"class": "stores__location-info"})
    for i in range(0,60):
        location_name = main[i].find("div", {"class": "stores__location-name"})
        hour1 = main[i].find("div", {"class": "stores__location-hours"}).text.strip()
        if hour1 is not '':
            hour = hour1.replace('\n', '')
           
        else:
            hour = '<MISSING>'
            
        if main[i].find("a") is not None:

            lat_tmp = main[i].find("a")['href']
            if len(lat_tmp.split("&sll=")) > 1:
                latitude = lat_tmp.split("&sll=")[1].split("&")[0].split(",")[0]
                longitude = lat_tmp.split("&sll=")[1].split("&")[0].split(",")[1]
            elif len(lat_tmp.split("/@")) > 1:
                latitude = lat_tmp.split("/@")[1].split(",")[0]
                longitude = lat_tmp.split("/@")[1].split(",")[1]
            else:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
           
        address_tmp = list(main[i].stripped_strings)
        # print(len(address_tmp))
        location_name = address_tmp[0]
        if (len(address_tmp)==5):
            location_name = address_tmp[0]
            address = address_tmp[1]
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
            city = state_tmp3[-2]
            state = state_tmp3[-1].strip()
            phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(address_tmp))[0]
        elif (len(address_tmp)==6):
            phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(address_tmp))[0]
            location_name =address_tmp[-5]
            address = address_tmp[-4]
            state_tmp = address_tmp[-3].split(',')
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
            state = state_tmp1.replace(zip,'').strip()
        else:
            location_name = address_tmp[0]
            address = address_tmp[1]
            state_tmp = address_tmp[2].split(',')
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
            state = state_tmp1.replace(zip,'').strip()
            phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(address_tmp))[0] 
            # print(phone)    
     
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
        tem_var.append('<MISSING>')
        return_main_object.append(tem_var)
     
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
