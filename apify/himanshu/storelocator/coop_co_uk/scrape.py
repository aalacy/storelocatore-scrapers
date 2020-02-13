import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests


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
    base_url = "https://finder.coop.co.uk/food/counties"
    addresses = []
    session = SgRequests()
    r1 = session.get(base_url)
    soup = BeautifulSoup(r1.text,"lxml")
    state = soup.find_all("ul",{"class":"three-column list-bare"})
    for data in state:
        for href in data.find_all("li"):
            r2 = session.get("https://finder.coop.co.uk"+href.find("a")['href'])
            soup1 = BeautifulSoup(r2.text,"lxml")
            for citys in (soup1.find_all("ul",{"class":"three-column list-bare"})):
                for li in citys.find_all("li"):
                    r3 = session.get("https://finder.coop.co.uk"+li.find("a")['href'])
                    soup3 = BeautifulSoup(r3.text,"lxml")
                    location_type1 = soup3.find("ul",{"class":"list--facilities"})
                    # location_type1 =''
                    # print("https://finder.coop.co.uk"+li.find("a")['href'])
                    # if location_type1 != None:
                    #     print(location_type1.text.strip().replace("\n",' '))
                    page_url = "https://finder.coop.co.uk"+li.find("a")['href']
                    streetAddress = ''
                    data2 = list(soup3.find("address",{"data-store-address-24":""}).stripped_strings)
                    stopwords =','
                    data1 = [word for word in data2 if word not in stopwords]
                    if len(data1)==3:
                        streetAddress = data1[0]
                        city = data1[1]
                        zip1 = data1[-1]
                    elif len(data1)==4:
                        streetAddress = " ".join(data1[:2])
                        city = data1[2]
                        zip1 = data1[-1]
                    # else:
                        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ",len(data1))
                        # print(data1)
                    try:
                        phone = soup3.find("a",{"class":"nowrap"}).text
                    except:
                        phone='<MISSING>'
                    try:
                        hours = soup3.find("div",{"id":"store-hours"}).text.strip().replace("\n"," ")
                    except:
                        hours ='<MISSING>'

                    name  = soup3.find("div",{"class":"info-card"}).find("h1").text.strip()
                    id1 = soup3.find("main",{"id":"main"}).attrs['data-store-id']
                    lat = soup3.find("main",{"id":"main"}).attrs['data-latlng-'+id1].split(",")[0]
                    lng = soup3.find("main",{"id":"main"}).attrs['data-latlng-'+id1].split(",")[-1]
                    tem_var =[]
                    tem_var.append("https://www.coop.co.uk")
                    tem_var.append(name.strip() if name.strip() else "<MISSING>")
                    tem_var.append(streetAddress if streetAddress.strip() else "<MISSING>")
                    tem_var.append(city.strip() if city.strip() else "<MISSING>")
                    tem_var.append("<MISSING>")
                    tem_var.append(zip1.strip() if zip1.strip() else "<MISSING>")
                    tem_var.append("UK")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone.strip() if phone.strip() else "<MISSING>")
                    tem_var.append("Co-op Food")
                    tem_var.append(lat)
                    tem_var.append(lng)
                    tem_var.append(hours if hours.strip() else "<MISSING>")
                    tem_var.append(page_url)
                    if tem_var[2] in addresses:
                        continue
                    addresses.append(tem_var[2])

                    # print("~~~~~~~~~~~~~~~~~~~~  ",tem_var)
                    yield tem_var

    
def scrape():
    data = fetch_data()
    write_output(data)


scrape()


