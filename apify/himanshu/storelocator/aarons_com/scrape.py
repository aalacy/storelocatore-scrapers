import json
import urllib.parse
import time
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
    store_name=[]
    store_detail=[]
    return_main_object=[]
    coutry="US"
    urls = ["https://locations.aarons.com/pr","https://locations.aarons.com/us","https://locations.aarons.com/ca"]
    for index,q in enumerate(urls):
        if index==0 or index==1:
            coutry = "US"
        else:
            coutry = "CA"
        r = requests.get(q)
        soup= BeautifulSoup(r.text,"lxml")
        k= soup.find_all("li",{"class":"Directory-listItem"})
        for i in k:
            link = i.find("a")['data-count'].split("(")[-1]
            if link != "1)":
                city_link = "https://locations.aarons.com/"+i.find("a")['href']
                r1 = requests.get(city_link)
                soup1= BeautifulSoup(r1.text,"lxml")
                citylink= soup1.find_all("li",{"class":"Directory-listItem"})
                for c in citylink:
                    link1 = c.find("a")['data-count'].split("(")[-1]
                    if link1 != "1)":
                        # print(link1)
                        sublink = "https://locations.aarons.com"+c.find("a")['href'].replace("..",'')
                        # print(sublink)
                        r2 = requests.get(sublink)
                        soup2= BeautifulSoup(r2.text,"lxml")
                        store_link = soup2.find_all("a",class_="Teaser-titleLink")
                        for st in store_link:
                            r3 = requests.get("https://locations.aarons.com"+st['href'].replace("..",""))
                            page_url = "https://locations.aarons.com"+st['href'].replace("..","")
                            soup3= BeautifulSoup(r3.text,"lxml")
                            streetAddress1=''
                            try:
                                streetAddress1 = soup3.find("span",{"class":"c-address-street-2"}).text.strip()
                            except:
                                streetAddress1=''
                            streetAddress = soup3.find("span",{"class":"c-address-street-1"}).text.strip()+' '+streetAddress1
                            state = soup3.find("abbr",{"class":"c-address-state"}).text
                            zip1 = soup3.find("span",{"class":"c-address-postal-code"}).text
                            city = soup3.find("span",{"class":"c-address-city"}).text
                            name = " ".join(list(soup3.find("span",{"class":"LocationName-brand"}).stripped_strings))
                            phone = soup3.find("div",{"itemprop":"telephone"}).text
                            hours = " ".join(list(soup3.find("table",{"class":"c-hours-details"}).find("tbody").stripped_strings))
                            latitude = soup3.find("meta",{"itemprop":"latitude"})['content']
                            longitude = soup3.find("meta",{"itemprop":"longitude"})['content']
                            tem_var =[]
                            tem_var.append("https://www.aarons.com/")
                            tem_var.append(name)
                            tem_var.append(streetAddress)
                            tem_var.append(city)
                            tem_var.append(state)
                            tem_var.append(zip1)
                            tem_var.append(coutry)
                            tem_var.append("<MISSING>")
                            tem_var.append(phone)
                            tem_var.append("<MISSING>")
                            tem_var.append(latitude)
                            tem_var.append(longitude)
                            tem_var.append(hours)
                            tem_var.append(page_url)
                            yield tem_var
                            # print("========================================",tem_var)
                    else:
                        one_link="https://locations.aarons.com"+c.find("a")['href'].replace("..",'')
                        page_url = one_link
                        r4 = requests.get(one_link)
                        soup4= BeautifulSoup(r4.text,"lxml")
                        streetAddress1=''
                        try:
                            streetAddress1 = soup4.find("span",{"class":"c-address-street-2"}).text.strip()
                        except:
                            streetAddress1=''
                        streetAddress = soup4.find("span",{"class":"c-address-street-1"}).text.strip()+' '+streetAddress1
                        state = soup4.find("abbr",{"class":"c-address-state"}).text
                        zip1 = soup4.find("span",{"class":"c-address-postal-code"}).text
                        city = soup4.find("span",{"class":"c-address-city"}).text
                        name = " ".join(list(soup4.find("span",{"class":"LocationName-brand"}).stripped_strings))
                        phone = soup4.find("div",{"itemprop":"telephone"}).text
                        hours = " ".join(list(soup4.find("table",{"class":"c-hours-details"}).find("tbody").stripped_strings))
                        latitude = soup4.find("meta",{"itemprop":"latitude"})['content']
                        longitude = soup4.find("meta",{"itemprop":"longitude"})['content']
                        tem_var =[]
                        tem_var.append("https://locations.aarons.com/")
                        tem_var.append(name)
                        tem_var.append(streetAddress)
                        tem_var.append(city)
                        tem_var.append(state)
                        tem_var.append(zip1)
                        tem_var.append(coutry)
                        tem_var.append("<MISSING>")
                        tem_var.append(phone)
                        tem_var.append("<MISSING>")
                        tem_var.append(latitude)
                        tem_var.append(longitude)
                        tem_var.append(hours)
                        tem_var.append(page_url)
                        yield tem_var
                        # print("========================================",tem_var)
            else:

                
                one_link1 = "https://locations.aarons.com/"+i.find("a")['href']
                if "https://locations.aarons.com/pr" in q:
                    one_link1="https://locations.aarons.com/pr/rio-grande/centro-comercial-alturas-de-rio-grande"
                page_url = one_link1
                r5 = requests.get(one_link1)
                soup5= BeautifulSoup(r5.text,"lxml")
                streetAddress1=''
                try:
                    streetAddress1 = soup5.find("span",{"class":"c-address-street-2"}).text.strip()
                except:
                    streetAddress1=''
                streetAddress = soup5.find("span",{"class":"c-address-street-1"}).text.strip()+' '+streetAddress1
                try:
                    state = soup5.find("abbr",{"class":"c-address-state"}).text
                except:
                    state="<MISSING>"
                zip1 = soup5.find("span",{"class":"c-address-postal-code"}).text
                city = soup5.find("span",{"class":"c-address-city"}).text
                name = " ".join(list(soup5.find("span",{"class":"LocationName-brand"}).stripped_strings))
                phone = soup5.find("div",{"itemprop":"telephone"}).text
                hours = " ".join(list(soup5.find("table",{"class":"c-hours-details"}).find("tbody").stripped_strings))
                latitude = soup5.find("meta",{"itemprop":"latitude"})['content']
                longitude = soup5.find("meta",{"itemprop":"longitude"})['content']
                tem_var =[]
                tem_var.append("https://locations.aarons.com/")
                tem_var.append(name)
                tem_var.append(streetAddress)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zip1)
                tem_var.append(coutry)
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("<MISSING>")
                tem_var.append(latitude)
                tem_var.append(longitude)
                tem_var.append(hours)
                tem_var.append(page_url)
                yield tem_var
                # print("========================================",tem_var)
         
    

def scrape():
    data = fetch_data()
    write_output(data)


scrape()


