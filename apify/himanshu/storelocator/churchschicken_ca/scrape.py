import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import ast

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
    address =[]
    return_main_object=[]
    address1 =[]
    base_url= "https://www.churchschicken.ca/"
    # base_url = 'https://www.churchschicken.ca/british-columbia/locations/'
    r = requests.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    tag_store = soup.find_all(lambda tag: (tag.name == "span") and "Locations" == tag.text.strip())
    for tag in tag_store:
        if tag.parent['href'] in address:
            continue
        address.append(tag.parent['href'])
        # print(tag.parent['href'])
        r1 = requests.get(tag.parent['href'],headers=headers)
        soup1= BeautifulSoup(r1.text,"lxml")
        for link in soup1.find("div",{"class":"fusion-alignright"}).find_all('li'):
            if link.find("a")['href'] in address1:
                continue
            address1.append(link.find("a")['href'])
            if "/locations/" in link.find("a")['href']:
                if "https://www.churchschicken.ca/ontario/locations/"==link.find("a")['href'] or "https://www.churchschicken.ca/british-columbia/locations/" == link.find("a")['href']:
                    pass
                else:
                    r2 = requests.get(link.find("a")['href'],headers=headers)
                    page_url = link.find("a")['href']
                    # print(link.find("a")['href'])
                    soup2 = BeautifulSoup(r2.text,"lxml")
                    for q in soup2.find_all("script",{"type":"text/javascript"}):
                        if "var markers " in q.text:
                            lat = q.text.split("fusion_maps(")[1].split(");")[0].split('"latitude":')[1].split('"longitude":')[0].replace('"',"").replace(',',"")
                            lng = (q.text.split("fusion_maps(")[1].split(");")[0].split('"longitude":')[1].split("}],")[0].replace('"',''))
                    # print(list(soup2.find_all("div",{"class":"fusion-text"})[0].stripped_strings)[:])
                    # ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(list(soup2.find_all("div",{"class":"fusion-text"})[0].stripped_strings)[-3:]))
                    len1 = list(soup2.find_all("div",{"class":"fusion-text"})[0].stripped_strings)
                    state =''
                    try:
                        phone = list(soup2.find_all("div",{"class":"fusion-text"})[1].stripped_strings)[-1]
                    except:
                        phone = "<MISSING>"
                    try:
                        hours = " ".join(list(soup2.find_all("div",{"class":"fusion-text"})[2].stripped_strings)).replace("\xa0","")
                    except:
                        hours = '<MISSING>'
                    if len1[1][0].isdigit():
                        name  = len1[0]
                        st = len1[1]
                        city = len1[2].replace("ON","")
                        state_list = re.findall(r' ([A-Z]{2})', str(len1[-1]))
                        
                        #  state_list[-1]
                        # if state_list:
                        #     state = len1[-1].split(" ")[0]
                        # else:
                        #     state = len1[-2].split(" ")[-1]

                        state = len1[-1].replace("L6Y 4M3","ON").split(" ")[0]
                
                        # print(state)
                        # print("line1111111111 ",len1)
                        # print("statttttttttt ",state)
                        # print("lllllllllllllllllen ",len1[-1])
                        # print("state_liststate_list   ",state_list)
                        
                        ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(len1[3]))
                        if ca_zip_list:
                            zipp = ca_zip_list[-1]
                            country_code = "CA"
                    
                    else:
                        if len(len1[-1])==10:
                            state = len1[-1].split( )[0]
                            zipp = " ".join(len1[-1].split( )[1:])
                            city = len1[-2].replace(",","")
                            st = len1[0]
                        else:
                            zipp  = len1[-1]
                            state_list = re.findall(r' ([A-Z]{2})', str(len1[-2]))
                            if state_list:
                                state = state_list[-1]
                                st = " ".join(len1[:-2])
                                city = len1[-2].replace(state,"")
                                # print(city)

                    tem_var =[]
                    tem_var.append("https://www.churchschicken.ca")
                    tem_var.append(name if name else "<MISSING>")
                    tem_var.append(st)
                    tem_var.append(city)
                    tem_var.append(state.strip().lstrip() if state.strip().lstrip() else "<MISSING>")
                    tem_var.append(zipp)
                    tem_var.append("CA")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("churchschicken")
                    tem_var.append(lat)
                    tem_var.append(lng)
                    tem_var.append(hours)
                    tem_var.append(page_url)
                    # print("=============================================",tem_var)
                    yield tem_var
     
  


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


