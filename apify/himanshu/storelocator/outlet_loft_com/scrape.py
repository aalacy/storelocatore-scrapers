import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url= "https://stores.loft.com/outlet/index.html"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]

    k= soup.find_all("li",{"class":"c-directory-list-content-item"})
    for i in k:
        link = i.text.split("(")[-1]
        if link != "1)":
            city_link = "https://stores.loft.com/"+i.find("a")['href'].replace("..","")
            r1 = session.get(city_link)
            soup1= BeautifulSoup(r1.text,"lxml")
            citylink= soup1.find_all("li",{"class":"c-directory-list-content-item"})
            # print(citylink)
            for c in citylink:
                link1 = c.text.split("(")[-1]
                if link1 != "1)":
                    sublink = "https://stores.loft.com/"+c.find("a")['href'].replace("..","")
                    r2 = session.get(sublink)
                    soup2= BeautifulSoup(r2.text,"lxml")
                    store_link = soup2.find_all("a",class_="c-location-grid-item-link visit-page-YA")
                    for st in store_link:
                        # print(st['href'].replace("..","").replace("//",""))
                        r3 = session.get("https://stores.loft.com/"+st['href'].replace("..","").replace("//",""))
                        page_url ="https://stores.loft.com/"+st['href'].replace("..","").replace("//","")
                        soup3= BeautifulSoup(r3.text,"lxml")
                        if soup3.find("h2",{"class":"closed-title"}):
                            continue

                        streetAddress = soup3.find("span",{"itemprop":"streetAddress"}).text.strip()
                        state = soup3.find("span",{"itemprop":"addressRegion"}).text
                        zip1 = soup3.find("span",{"itemprop":"postalCode"}).text
                        city = soup3.find("span",{"itemprop":"addressLocality"}).text
                        name = " ".join(list(soup3.find("h1",{"itemprop":"name"}).stripped_strings))
                        phone = soup3.find("span",{"itemprop":"telephone"}).text
                        hours = " ".join(list(soup3.find("table",{"class":"c-location-hours-details"}).find("tbody").stripped_strings))
                        latitude = soup3.find("meta",{"itemprop":"latitude"})['content']
                        longitude = soup3.find("meta",{"itemprop":"longitude"})['content']
                        
                        tem_var =[]
                        tem_var.append("https://outlet.loft.com/")
                        tem_var.append(name)
                        tem_var.append(streetAddress)
                        tem_var.append(city.replace(",",""))
                        tem_var.append(state)
                        tem_var.append(zip1.strip())
                        tem_var.append("US")
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
                    # print(c.find("a")['href'])
                    # pass
                    one_link="https://stores.loft.com"+c.find("a")['href'].replace("..","")
                    page_url = one_link
                    # print(page_url)
                    r4 = session.get(one_link)
                    soup4= BeautifulSoup(r4.text,"lxml")
                    if soup4.find("h2",{"class":"closed-title"}):
                        continue

                    streetAddress = soup4.find("span",{"itemprop":"streetAddress"}).text.strip()
                    state = soup4.find("span",{"itemprop":"addressRegion"}).text
                    zip1 = soup4.find("span",{"itemprop":"postalCode"}).text
                    city = soup4.find("span",{"itemprop":"addressLocality"}).text
                    name = " ".join(list(soup4.find("h1",{"itemprop":"name"}).stripped_strings))
                    phone = soup4.find("span",{"itemprop":"telephone"}).text
                    try:
                        hours = " ".join(list(soup4.find("table",{"class":"c-location-hours-details"}).find("tbody").stripped_strings))
                    except:
                        hours = "<MISSING>"
                    latitude = soup4.find("meta",{"itemprop":"latitude"})['content']
                    longitude = soup4.find("meta",{"itemprop":"longitude"})['content']
        
                    tem_var =[]
                    tem_var.append("https://outlet.loft.com/")
                    tem_var.append(name)
                    tem_var.append(streetAddress)
                    tem_var.append(city.replace(",",""))
                    tem_var.append(state)
                    tem_var.append(zip1.strip())
                    tem_var.append("US")
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
            # print(i.find("a")['href'].replace("..",""))
            # print("https://stores.loft.com/"+i.find("a")['href'].replace("..",""))
            one_link1 = "https://stores.loft.com/"+i.find("a")['href'].replace("..","")
            page_url = one_link1
            r5 = session.get(one_link1)
            # print("--------------------------")
        
            soup5= BeautifulSoup(r5.text,"lxml")
            if soup5.find("h2",{"class":"closed-title"}):
                continue
            streetAddress = soup5.find("span",{"itemprop":"streetAddress"}).text.strip()
            state = soup5.find("span",{"itemprop":"addressRegion"}).text
            zip1 = soup5.find("span",{"itemprop":"postalCode"}).text
            city = soup5.find("span",{"itemprop":"addressLocality"}).text
            name = " ".join(list(soup5.find("h1",{"itemprop":"name"}).stripped_strings))
            phone = soup5.find("span",{"itemprop":"telephone"}).text
            try:
                hours = " ".join(list(soup5.find("table",{"class":"c-location-hours-details"}).find("tbody").stripped_strings))
            except:
                hours = "<MISSING>"
            latitude = soup5.find("meta",{"itemprop":"latitude"})['content']
            longitude = soup5.find("meta",{"itemprop":"longitude"})['content']
        
            tem_var =[]
            tem_var.append("https://outlet.loft.com/")
            tem_var.append(name)
            tem_var.append(streetAddress)
            tem_var.append(city.replace(",",""))
            tem_var.append(state)
            tem_var.append(zip1.strip())
            tem_var.append("US")
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


