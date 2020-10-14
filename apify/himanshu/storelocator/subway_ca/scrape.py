import json
import time
import csv
# import requests
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open(r'data.csv', mode='w',newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)





def fetch_data():
    base_url= "https://restaurants.subway.com/canada"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_detail=[]

    k = soup.find_all("a",{"class":"Directory-listLink","href":re.compile("canada/")})
    for i in k:
        
        link = i['data-count'].split("(")[-1]
        if link != "1)":
            city_link = "https://restaurants.subway.com/"+i['href']
            try:
                r1 = session.get(city_link)
            except:
                # print("city_link:--------- eorr",city_link)
                pass
            soup1= BeautifulSoup(r1.text,"lxml")
            citylink= soup1.find_all("a",{"class":"Directory-listLink","href":re.compile("../canada/")})
            
            for c in citylink:
                link1 = c['data-count'].split("(")[-1]
                if link1 != "1)":
                    sublink = "https://restaurants.subway.com"+c['href'].replace("..","").replace("///",'')
                    try:
                        r2 = session.get(sublink)
                    except:
                        # print("sublink:----------error ",sublink)
                        pass
                    soup2= BeautifulSoup(r2.text,"lxml")
                    store_link = soup2.find_all("a",{"class":"Teaser-title","data-ya-track":"visitpage"})
                    for st in store_link:
                        try:
                            r3 = session.get("https://restaurants.subway.com/"+st['href'].replace("..","").replace("///",''))
                            page_url = "https://restaurants.subway.com/"+st['href'].replace("..","").replace("///",'')
                        except:
                            pass
                            # print("page_url:------------- ",page_url)
                       
                        soup3= BeautifulSoup(r3.text,"lxml")
                        streetAddress = soup3.find("meta",{"itemprop":"streetAddress"})['content']
                        state = soup3.find("abbr",{"class":"c-address-state"}).text
                        zip1 = soup3.find("span",{"class":"c-address-postal-code"}).text
                        city = soup3.find("span",{"class":"c-address-city"}).text
                        name = " ".join(list(soup3.find("h1",{"class":"Heading--lead Hero-heading"}).stripped_strings))
                        try:
                            phone = soup3.find("div",{"itemprop":"telephone"}).text
                        except:
                            phone="<MISSING>"
                        hours = " ".join(list(soup3.find("table",{"class":"c-hours-details"}).find("tbody").stripped_strings))
                        latitude = soup3.find("meta",{"itemprop":"latitude"})['content']
                        longitude = soup3.find("meta",{"itemprop":"longitude"})['content']
                        tem_var =[]
                        tem_var.append("http://subway.ca")
                        tem_var.append(name)
                        tem_var.append(streetAddress)
                        tem_var.append(city)
                        tem_var.append(state)
                        tem_var.append(zip1)
                        tem_var.append("CA")
                        tem_var.append("<MISSING>")
                        tem_var.append(phone)
                        tem_var.append("<MISSING>")
                        tem_var.append(latitude)
                        tem_var.append(longitude)
                        tem_var.append(hours)
                        tem_var.append(page_url.replace("///",'/'))
                        # yield tem_var
                        store_detail.append(tem_var)
                        # print("========================================",tem_var)

                else:
                    try:
                        one_link="https://restaurants.subway.com"+c['href'].replace("..",'').replace("///",'/')
                        page_url = one_link.replace("///",'/')
                    except:
                        pass
                  
                    r4 = session.get(one_link)
                    soup4= BeautifulSoup(r4.text,"lxml")
                    streetAddress = soup4.find("meta",{"itemprop":"streetAddress"})['content']
                    state = soup4.find("abbr",{"class":"c-address-state"}).text
                    zip1 = soup4.find("span",{"class":"c-address-postal-code"}).text
                    city = soup4.find("span",{"class":"c-address-city"}).text
                    name = " ".join(list(soup4.find("h1",{"class":"Heading--lead Hero-heading"}).stripped_strings))
                    try:
                        phone = soup4.find("div",{"itemprop":"telephone"}).text
                    except:
                        phone="<MISSING>"
                    hours = " ".join(list(soup4.find("table",{"class":"c-hours-details"}).find("tbody").stripped_strings))
                    latitude = soup4.find("meta",{"itemprop":"latitude"})['content']
                    longitude = soup4.find("meta",{"itemprop":"longitude"})['content']
                    
                    tem_var =[]
                    tem_var.append("http://subway.ca")
                    tem_var.append(name)
                    tem_var.append(streetAddress)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zip1)
                    tem_var.append("CA")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("<MISSING>")
                    tem_var.append(latitude)
                    tem_var.append(longitude)
                    tem_var.append(hours)
                    tem_var.append(page_url.replace("///",'/'))
                    # yield tem_var
                    store_detail.append(tem_var)
                    # print("========================================",tem_var)
        else:
            one_link1 = "https://restaurants.subway.com/"+c['href']
            page_url = one_link1
            r5 = session.get(one_link1)
            soup5= BeautifulSoup(r5.text,"lxml")
            streetAddress = soup5.find("meta",{"itemprop":"streetAddress"})['content']
            state = soup5.find("abbr",{"class":"c-address-state"}).text
            zip1 = soup5.find("span",{"class":"c-address-postal-code"}).text
            city = soup5.find("span",{"class":"c-address-city"}).text
            name = " ".join(list(soup5.find("h1",{"class":"Heading--lead Hero-heading"}).stripped_strings))
            try:
                phone = soup5.find("div",{"itemprop":"telephone"}).text
            except:
                phone="<MISSING>"
            hours = " ".join(list(soup5.find("table",{"class":"c-hours-details"}).find("tbody").stripped_strings))
            latitude = soup5.find("meta",{"itemprop":"latitude"})['content']
            longitude = soup5.find("meta",{"itemprop":"longitude"})['content']
            
            tem_var =[]
            tem_var.append("http://subway.ca")
            tem_var.append(name)
            tem_var.append(streetAddress)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zip1)
            tem_var.append("CA")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append(latitude)
            tem_var.append(longitude)
            tem_var.append(hours)
            tem_var.append(page_url.replace("///",'/'))
            # yield tem_var
            store_detail.append(tem_var)
            # print("========================================",tem_var)
    dub=[]
    for i in range(len(store_detail)):
        if str(store_detail[i][2]+store_detail[i][-1]) in dub:
            continue
        dub.append(store_detail[i][2]+store_detail[i][-1])
        yield store_detail[i]




def scrape():
    data = fetch_data()
    write_output(data)


scrape()


