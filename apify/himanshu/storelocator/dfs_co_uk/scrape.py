import csv
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
import requests

session = SgRequests()



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }

    base_url = "https://www.dfs.co.uk/"
    r =  session.get("https://www.dfs.co.uk/store-directory", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")    
    for link in soup.find_all("a",{"class":"btn-xl button primary moreBttonRight"}):
        page_url = link['href']
        try:
            page_url = link['href']
            # print(page_url)
            r1 = session.get(page_url, headers=headers)
            soup1 = BeautifulSoup(r1.text, "lxml")
            location_name = soup1.find("h3",{"class":"legalName"}).text.strip()
            street_address = re.sub(r'\s+'," ",soup1.find("span",{"itemprop":"streetAddress"}).text)
            try:
                city = soup1.find("span",{"itemprop":"addressLocality"}).text.strip()
            except:
                city = "<MISSING>"
            state = soup1.find("span",{"itemprop":"addressRegion"}).text.strip()
            zipp = soup1.find("span",{"itemprop":"postalCode"}).text.strip()
            phone = re.sub(r'\s+'," ",soup1.find("p",{"class":"contact"}).find("a")['href'].split("tel:")[-1])
            store_number = soup1.find("input",{"name":"stLocId"})['value']
            coord = soup1.find(lambda tag: (tag.name== "script") and "latitude" in tag.text).text
            latitude = coord.split('"latitude":')[1].split(",")[0].strip()
            longitude = coord.split('"longitude":')[1].split("}")[0].strip()
            hours_of_operation = re.sub(r'\s+'," "," ".join(list(soup1.find("div",{"class":"KstoreOpening"}).stripped_strings)))

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address.replace(city,""))
            store.append(city)
            store.append(state if state else "<MISSING>")
            store.append(zipp)
            store.append("UK")
            store.append(store_number)
            store.append(phone )
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            # print("data===="+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
            yield store

        except:
            r2 = session.get(page_url)
            soup2 = BeautifulSoup(r2.text, "lxml")
            for link in soup2.find_all("a",{"class":"btn-xl button primary moreBttonRight"}):
                page_url = link['href']
                # print(page_url)
                r3 = session.get(page_url)
                soup3 = BeautifulSoup(r3.text, "lxml")
                location_name = soup3.find("h3",{"class":"legalName"}).text.strip()
                
                street_address = re.sub(r'\s+'," ",soup3.find("span",{"itemprop":"streetAddress"}).text)
                
                try:
                    city = soup3.find("span",{"itemprop":"addressLocality"}).text.strip()
                except:
                    city = "<MISSING>"
                state = soup3.find("span",{"itemprop":"addressRegion"}).text.strip()
                zipp = soup3.find("span",{"itemprop":"postalCode"}).text.strip()
                phone = re.sub(r'\s+'," ",soup3.find("p",{"class":"contact"}).find("a")['href'].split("tel:")[-1])
                store_number = soup3.find("input",{"name":"stLocId"})['value']
                coord = soup3.find(lambda tag: (tag.name== "script") and "latitude" in tag.text).text
                latitude = coord.split('"latitude":')[1].split(",")[0].strip()
                longitude = coord.split('"longitude":')[1].split("}")[0].strip()
                hours_of_operation = re.sub(r'\s+'," "," ".join(list(soup3.find("div",{"class":"KstoreOpening"}).stripped_strings)))

   
                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address.replace(city,""))
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append("UK")
                store.append(store_number)
                store.append(phone )
                store.append("<MISSING>")
                store.append(latitude)
                store.append(longitude)
                store.append(hours_of_operation)
                store.append(page_url)
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                # print("data===="+str(store))
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
