
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
from datetime import datetime
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data(): 

    base_url = "https://www.uri.com/"


    url_lst = ["https://www.uri.com/INTERSHOP/web/WFS/URI-URIUS-Site/en_US/-/USD/ViewStoreFinder-All?Name=L&Com=adr&Db=DLRUnited&Ds=&RT=lo&Filt=User10%3C%3E%27W%27&oldZip=&oldCity=&oldState=&zipLatitude=&zipLongitude=&physLatitude=&physLongitude=&branchError=Invalid+entry&branchStates=&cityData=&stateData=&showEmergency=false&SKU=&homePage=false&searchInput=AL&Zp=&Ci=&St=AL&searchButton=Search","https://www.uri.com/INTERSHOP/web/WFS/URI-URIUS-Site/en_US/-/USD/ViewPage-CanadaBranchLocations"]
    
    for url in url_lst:
        soup = bs(session.get(url).content, "lxml")
        if "CanadaBranchLocations" in url:
            for div in soup.find_all("div",{"class":"cta-container col-sm-12 col-md-4 col-xs-12"}):
                location_name = div.find("div",{"class":"title"}).text

                addr = list(div.find("div",{"class":"details"}).stripped_strings)
                street_address = addr[0]
                city = addr[1].split(",")[0]
                state = addr[1].split(",")[1].split()[0]
                zipp = " ".join(addr[1].split(",")[1].split()[1:])
                phone = addr[3]
                hours = " ".join(addr[6:8])
                
                coords = session.get(div.find("a",{"class":"outline"})['href']).url
                lat = coords.split("@")[1].split(",")[0]
                lng = coords.split("@")[1].split(",")[1]

                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)   
                store.append("CA")
                store.append("<MISSING>")
                store.append(phone)
                store.append("<MISSING>")
                store.append(lat)
                store.append(lng)
                store.append(hours)
                store.append(url)     
            
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                yield store
        else:
            name = soup.find_all("td",{"class":"branchname"})
            address = soup.find_all("td",{"class":"branchaddress"})
            locality = soup.find_all("td",{"class":"branchcity"})
            region = soup.find_all("td",{"class":"branchstate"})
            postal_code = soup.find_all("td",{"class":"branchzip"})
            country = soup.find_all("td",{"class":"branchcountry"})
            phone = soup.find_all("td",{"class":"branchphone"})
            storenumber = soup.find_all("td",{"class":"branchid"})
            lat = soup.find_all("td",{"class":"branchlatitude"})
            lng = soup.find_all("td",{"class":"branchlongitude"})
            hours1 = soup.find_all("td",{"class":"branchmfhours"})
            hours2 = soup.find_all("td",{"class":"branchhours"})

            for index,data in enumerate(name):
                store = []
                store.append(base_url)
                store.append(data.text)
                store.append(address[index].text)
                store.append(locality[index].text)
                store.append(region[index].text)
                store.append(postal_code[index].text)
                store.append(country[index].text)
                store.append(storenumber[index].text.split()[0].replace("#","").strip() if storenumber[index].text.split()[0].replace("#","").strip().isdigit() else "<MISSING>" )
                store.append(phone[index].text)
                store.append("<MISSING>")
                store.append(lat[index].text)
                store.append(lng[index].text)
                store.append("Open Monday through Friday: "+ hours1[index].text+ " Saturday Hours: "+ hours2[index].text)
                store.append("<MISSING>")
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                yield store
   
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
