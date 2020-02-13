import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import ast
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from random import choice

# def get_driver():
#     options = Options()
#     # options.add_argument('--headless')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--window-size=1920,1080')
#     return webdriver.Firefox(executable_path='geckodriver.exe', options=options)
def get_proxy():
    url = "https://www.sslproxies.org/"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html5lib")
    return {'https': (choice(list(map(lambda x:x[0]+':'+x[1],list(zip(map(lambda x:x.text,soup.findAll('td')[::8]),map(lambda x:x.text,soup.findAll('td')[1::8])))))))}
    

def proxy_request(request_type, url, **kwargs):
    while 1:
        try:
            proxy = get_proxy()
            # print("Using Proxy {}".format(proxy))
            r = requests.request(request_type, url, proxies=proxy, timeout=5, **kwargs)
            break
        except:
            pass
    return r

def write_output(data):
    with open('cityblueshop.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",'page_url'])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    # driver = get_driver()
    addresses =[]
    base_url = "https://www.cityblueshop.com/pages/locations"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    # soup = BeautifulSoup(driver.page_source, "lxml")
    # r = requests.get(base_url,headers=headers)

    # soup = BeautifulSoup(driver.page_source, "lxml")

    r = proxy_request("get",base_url,headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    # print(soup)
    for parts in soup.find_all("div", {"class": "rte-content colored-links"}):
        for semi_parts in parts.find_all("h3"):
            # print(semi_parts.find("a")['href'])
            phone1 =''
            store_request = requests.get(semi_parts.find("a")['href'])
            store_soup = BeautifulSoup(store_request.text, "lxml")
            page_url = semi_parts.find("a")['href']
            for inner_parts in store_soup.find_all("div", {"class": "rte-content colored-links"}):
                temp_storeaddresss = list(inner_parts.stripped_strings)
                location_name = semi_parts.text
                if len(temp_storeaddresss) ==7:
                    phone1 = temp_storeaddresss[2].replace("Ph: ","")
                    # print(temp_storeaddresss[2].replace("Ph: ",""))
                    street_address = temp_storeaddresss[0].replace("\xa0","")
                    
                    city = temp_storeaddresss[1].replace("\xa0","").split(',')[0]
                    state =  temp_storeaddresss[1].replace("\xa0","").split(',')[0].replace("19147",'')
                    zipcode =temp_storeaddresss[1].split(",")[-1].split( )[-1]
                    longitude = inner_parts.find("iframe")['src'].split("!2d")[-1].split("!3d")[0]
                    latitude = inner_parts.find("iframe")['src'].split("!2d")[-1].split("!3d")[-1].split("!2m")[0].split("!3m")[0]
                    hours = " ".join(temp_storeaddresss[-4:])
                    # print(temp_storeaddresss[1].split(",")[-1].split( )[-1])
                elif len(temp_storeaddresss) ==4:
                    if len(temp_storeaddresss[0].split(","))==2:
                        zipcode = temp_storeaddresss[0].split(",")[-1].split(" ")[-1]
                        state = temp_storeaddresss[0].split(",")[-1].split(" ")[-2]
                        city = temp_storeaddresss[0].split(",")[-1].split(" ")[-3]
                        hours = " ".join(temp_storeaddresss[-2:])
                        phone1 = temp_storeaddresss[-3]
                        
                        street_address= temp_storeaddresss[0].replace(" Wyncote PA 19095",'').replace(", DE 19703",'')
                        
                        longitude = inner_parts.find("iframe")['src'].split("!2d")[-1].split("!3d")[0]
                        latitude = inner_parts.find("iframe")['src'].split("!2d")[-1].split("!3d")[-1].split("!2m")[0].split("!3m")[0]
                        
                    elif len(temp_storeaddresss[0].split(","))==4:
                        state = temp_storeaddresss[0].split(",")[-1].split( )[-2]
                        zipcode = temp_storeaddresss[0].split(",")[-1].split( )[-1]
                        city = temp_storeaddresss[0].split(",")[-2]
                        street_address = " ".join(temp_storeaddresss[0].split(",")[:-2])
                        hours = " ".join(temp_storeaddresss[-2:])
                        phone1 = temp_storeaddresss[-3]
                        longitude = inner_parts.find("iframe")['src'].split("!2d")[-1].split("!3d")[0]
                        latitude = inner_parts.find("iframe")['src'].split("!2d")[-1].split("!3d")[-1].split("!2m")[0].split("!3m")[0]
                        
                        # print(latitude)
                        
                    elif len(temp_storeaddresss[0].split(","))==3:
                        street_address = temp_storeaddresss[0].split(",")[0]
                        city = temp_storeaddresss[0].split(",")[1]
                        # state = temp_storeaddresss[0].split(",")[2].split().strip().split( )[0]
                        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(temp_storeaddresss[0].split(",")[2]))
                        state_list = re.findall(r' ([A-Z]{2})', str(temp_storeaddresss[0].split(",")[2]))
                        if us_zip_list:
                            zipcode = us_zip_list[-1]

                        if state_list:
                            state = state_list[-1]
                        hours = " ".join(temp_storeaddresss[-2:])
                        phone1 = temp_storeaddresss[-3]
                        
                        longitude = inner_parts.find("iframe")['src'].split("!2d")[-1].split("!3d")[0]
                        latitude = inner_parts.find("iframe")['src'].split("!2d")[-1].split("!3d")[-1].split("!2m")[0].split("!3m")[0]

                elif len(temp_storeaddresss) ==5:
                    hours = " ".join(temp_storeaddresss[-2:])
                    
                    if "Mon" in temp_storeaddresss[-2]:
                        hours = " ".join(temp_storeaddresss[-2:])
                    if "Mon" in temp_storeaddresss[-3]:
                        hours = " ".join(temp_storeaddresss[-3:])
                    street_address = temp_storeaddresss[0].split(",")[0]
                    
                    phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(temp_storeaddresss))
                    if phone_list:
                        phone1 = phone_list[-1]
                    
                    temp_storeaddresss.remove(phone1)
                    new = temp_storeaddresss[:-2]
                    if "Mon" in new[-1]:
                        del new[-1]
                    state = new[-1].split(",")[-2]
                    zipcode = new[-1].split(",")[-1].strip().split( )[-1]
                    city = new[-1].split(",")[-2]
                    # street_address = new[-1].split(",")[0]
                    print("~~~~~~~~~~~~~~~~~~~~~",street_address)
                    longitude = inner_parts.find("iframe")['src'].split("!2d")[-1].split("!3d")[0]
                    latitude = inner_parts.find("iframe")['src'].split("!2d")[-1].split("!3d")[-1].split("!2m")[0].split("!3m")[0]

            return_object =[]
            if "1330 Franklin Mills Circle" in street_address:
                pass
            else:
                return_object.append("https://www.cityblueshop.com")
                return_object.append(location_name.encode('ascii', 'ignore').decode('ascii').strip() if location_name else "<MISSING>")
                return_object.append(street_address.encode('ascii', 'ignore').decode('ascii').strip() if street_address else "<MISSING>")
                return_object.append(city.encode('ascii', 'ignore').decode('ascii').strip() if city else "<MISSING>")
                return_object.append(state.encode('ascii', 'ignore').decode('ascii').strip().replace("Philadelphia","PA").replace("Upper Darby","PA").replace("East Cleveland","HO").replace("North Randall","HO") if state.replace("Philadelphia","PA").replace("Upper Darby","PA").replace("Upper Darby","PA") else "<MISSING>")
                return_object.append(zipcode if zipcode else "<MISSING>")
                return_object.append("US")
                return_object.append("<MISSING>")
                return_object.append(str(phone1).encode('ascii', 'ignore').decode('ascii').strip().replace("Ph:","") if phone1 else "<MISSING>")
                return_object.append("<MISSING>")
                return_object.append(latitude if latitude else "<MISSING>")
                return_object.append(longitude if longitude else "<MISSING>")
                return_object.append(hours.encode('ascii', 'ignore').decode('ascii').strip() if hours else "<MISSING>")
                return_object.append(page_url)
                # print("return_object---------------------  ",return_object)
                if return_object[2] in addresses:
                    continue
                addresses.append(return_object[2])
                yield return_object


def scrape():
    data = fetch_data()
    write_output(data)

scrape()


