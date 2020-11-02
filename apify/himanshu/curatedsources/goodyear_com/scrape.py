import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('goodyear_com')



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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',

    }
    return_main_object=[]
    addressess =[]
    base_url= 'https://www.goodyear.com'
    get_url= "https://www.goodyear.com/en-US/tires/tire-shop"        
    r = requests.get(get_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    all_city = []
    for i in soup.find("ul",{"id":"hiddenRegions"}).find_all('li'):
        link=base_url+i.find('a')['href']
        # logger.info(i.find('a').text,"city===============================","https://www.goodyear.com"+i.find('a')['href'])
        try:
            r1 = requests.get(link,headers=headers)
            soup1= BeautifulSoup(r1.text,"lxml")
        except:
            pass
        for city in soup1.find("div",{'class':"list-group row"}).find_all("li"):
            # logger.info(city.text,'--------store-----------------------',"https://www.goodyear.com"+city.find("a")['href'])
          
            try:
                r2 = requests.get("https://www.goodyear.com"+city.find("a")['href'],headers=headers)
            except:
                pass
            soup2= BeautifulSoup(r2.text,"lxml")
            # all_city13 = soup2.find_all('a',{"class":"gy-link store-name-link link-chevron"})
            for store1 in soup2.find_all('a',{"class":"gy-link store-name-link link-chevron"}):
                # logger.info(store1)
                tem_var =[]
                try:
                    # logger.info("--------------store----------------","https://www.goodyear.com"+store1['href'])
                    r3 = requests.get("https://www.goodyear.com"+store1['href'],headers=headers)
                except:
                    pass
                soup3= BeautifulSoup(r3.text,"lxml")
                address = soup3.find("span",{"class":"address-street"})
                city = soup3.find("span",{"class":"address-city-state"})
                zipcode = soup3.find("span",{"class":"address-zipcode"}).text
                phone = soup3.find("a",{"itemprop":"telephone"})
                hours = soup3.find("div",{"class":"store-hours col-sm-6"})
                name = soup3.find("h1",{"itemprop":"name"}).text.strip().lstrip()
                name1 = " ".join(name.split("---"))
                if hours != None:
                    hours1 = " ".join(list(hours.stripped_strings))
                if phone != None:
                    phone1 = phone.text
                if address != None:
                    address1 = address.text
                city1 = city.text.split(",")[0]
                state1 = city.text.split(",")[1].replace("\xa0","")
                all_script =soup3.find_all("script",{"type":"text/javascript"})
                for script in all_script:
                    if "window.jsonObjects.storeData" in script.text:
                        json_data = json.loads(script.text.split("window.jsonObjects.storeData = ")[1].replace("};","}"))
                        latitude = json_data['latitude']
                        longitude = json_data['longitude']
                tem_var.append("https://www.goodyear.com")
                tem_var.append(name1.encode('ascii', 'ignore').decode('ascii').strip() if name1 else "<MISSING>")
                tem_var.append(address1.encode('ascii', 'ignore').decode('ascii').strip() if address1 else "<MISSING>")
                tem_var.append(city1.encode('ascii', 'ignore').decode('ascii').strip() if city1 else "<MISSING>")
                tem_var.append(state1.encode('ascii', 'ignore').decode('ascii').strip() if state1 else "<MISSING>")
                tem_var.append(zipcode.encode('ascii', 'ignore').decode('ascii').strip() if zipcode else "<MISSING>")
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone1.encode('ascii', 'ignore').decode('ascii').strip() if phone1 else "<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(str(latitude).encode('ascii', 'ignore').decode('ascii').strip() if str(latitude) else "<MISSING>")
                tem_var.append(str(longitude).encode('ascii', 'ignore').decode('ascii').strip() if str(longitude) else "<MISSING>")
                tem_var.append(hours1.encode('ascii', 'ignore').decode('ascii').strip() if  hours1 else "<MISSING>")
                tem_var.append("https://www.goodyear.com"+store1['href'])
                if tem_var[2] in addressess:
                    continue
                addressess.append(tem_var[2])
                # logger.info("===================================================",tem_var)
                yield tem_var
    

def scrape():
    data = fetch_data()
    write_output(data)


scrape()



