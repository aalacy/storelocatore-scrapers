import csv
import re
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
session = SgRequests()
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('skyscanner_ca')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url", "website", "IATA_code", "ICAO_code"])
        # Body
        for row in data:
            writer.writerow(row)


def dms2dd(degrees, minutes, seconds, direction):
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60)
    if direction == 'S' or direction == 'W':
        dd *= -1
    return dd

def dd2dms(deg):
    d = int(deg)
    md = abs(deg - d) * 60
    m = int(md)
    sd = (md - m) * 60
    return [d, m, sd]

def parse_dms(dms):
    parts = re.split('[^\d\w]+', dms)
    lat = dms2dd(parts[0], parts[1], parts[2], parts[3])

    return (lat)

def fetch_data():
    base_url = "https://www.skyscanner.ca"

    r = requests.get("https://www.skyscanner.ca/airports/ca/airports-in-canada.html")
    soup = BeautifulSoup(r.text, "lxml")
    for link in soup.find("table",{"class":"sm_table sm_table_sections3"}).find_all("a"):
        url = base_url+link['href']
        r1 = requests.get(url)
        soup1 = BeautifulSoup(r1.text, "lxml")     
        if soup1.find("div",{"class":"lhs_info"}):
            for link in soup1.find("div",{"class":"lhs_info"}).find("ul").find_all("a"):
                page_url = base_url+link['href']
                r2 = requests.get(page_url)
                soup2 = BeautifulSoup(r2.text, "lxml")
                location_name = soup2.find("h1",{"class":"t"}).text.strip().replace("CA:","")
                data = list(soup2.find_all("div",{"class":"content"})[-2].stripped_strings)
                if len(data) == 7:
                    ICAO_code = "<MISSING>"
                    IATA_code = data[-2]

                else:
                    ICAO_code = data[-1]
                    IATA_code = data[-3]

                latitude = soup2.find("meta",{"property":"place:location:latitude"})['content']
                longitude = soup2.find("meta",{"property":"place:location:longitude"})['content']
               
                if soup2.find("div",{"id":"a_details"}):
                    if soup2.find("div",{"id":"a_details"}).find("td",{"itemprop":"telephone"}):
                        phone = soup2.find("div",{"id":"a_details"}).find("td",{"itemprop":"telephone"}).text   
                    else:
                        phone = "<MISSING>"
                    if soup2.find("div",{"id":"a_details"}).find("a",{"itemprop":"url"}):
                        website = soup2.find("div",{"id":"a_details"}).find("a",{"itemprop":"url"})['href']
                    else:
                        website = "<MISSING>"

                    p_tag = soup2.find("div",{"id":"a_details"}).find("div",{"class":"content"}).find_all("p")
                    if len(p_tag) == 0:
                        street_address = "<MISSING>"
                        city = "<MISSING>"
                        state = "<MISSING>"
                        zipp = "<MISSING>"
                    else:
                        addr = list(p_tag[0].stripped_strings)
                        if "Address:" in addr[0]:
                            del addr[0]
                        if "CANADA" in addr[-1]:
                            del addr[-1]
                        street_address = " ".join(addr[:-3])
                        city = addr[-3]
                        state = addr[-2]
                        zipp = addr[-1]
                   
                else:
                    street_address = "<MISSING>"
                    city = "<MISSING>"
                    state = "<MISSING>"
                    zipp = "<MISSING>"
                    phone = "<MISSING>"
                    website = "<MISSING>"
        else:
            page_url = url
            location_name = soup1.find("h1",{"class":"t"}).text.strip().split(":")[0]
            data = list(soup1.find_all("div",{"class":"content"})[-2].stripped_strings)
            if len(data) == 7:
                ICAO_code = "<MISSING>"
                IATA_code = data[-2]

            else:
                ICAO_code = data[-1]
                IATA_code = data[-3]
        
            latitude = soup1.find("meta",{"property":"place:location:latitude"})['content']
            longitude = soup1.find("meta",{"property":"place:location:longitude"})['content']
            
            if soup1.find("div",{"id":"a_details"}):
                if soup1.find("div",{"id":"a_details"}).find("td",{"itemprop":"telephone"}):
                    phone = soup1.find("div",{"id":"a_details"}).find("td",{"itemprop":"telephone"}).text
                else:
                    phone = "<MISSING>"
                if soup1.find("div",{"id":"a_details"}).find("a",{"itemprop":"url"}):
                    website = soup1.find("div",{"id":"a_details"}).find("a",{"itemprop":"url"})['href']
                else:
                    website = "<MISSING>"
                p_tag = soup1.find("div",{"id":"a_details"}).find("div",{"class":"content"}).find_all("p")
                if (len(p_tag)) == 1:
                    addr = (list(soup1.find("div",{"id":"a_details"}).find("div",{"class":"content"}).find_all("p")[0].stripped_strings))
                    if len(addr) == 2:
                        street_address = "<MISSING>"
                        city = "<MISSING>"
                        state = "<MISSING>"
                        zipp = "<MISSING>"
                    elif len(addr) == 4:
                        street_address = "<MISSING>"
                        city = addr[-3]
                        state = addr[-2]
                        zipp = "<MISSING>"
                    elif len(addr) == 9:
                        street_address = " ".join(addr[1:3]).replace("Address:","").strip()
                        city = addr[3]
                        state = addr[-2]
                        zipp = "<MISSING>"

                    else:
                        street_address = " ".join(addr[:-4]).replace("Address:","").strip()
                        city = addr[-4].replace("Lake Harbour","Baffin Island")
                        state = addr[-3].replace("Baffin Island","NT")
                        zipp = addr[-2].replace("NT","<MISSING>")
                else:

                    addr = (list(soup1.find("div",{"id":"a_details"}).find("div",{"class":"content"}).find_all("p")[0].stripped_strings))
                    if len(addr) == 5:
                        street_address = addr[1]
                        city = addr[2]
                        state = "<MISSING>"
                        zipp = addr[-2]
                    else:
                        street_address = " ".join(addr[:-4]).replace("Address:","").strip()
                        city = addr[-4]
                        state = addr[-3]
                        zipp = addr[-2]
                    
            else:
                street_address = "<MISSING>"
                city = "<MISSING>"
                state = "<MISSING>"
                zipp = "<MISSING>"
                phone = "<MISSING>"
                website = "<MISSING>"
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address.replace(",","") if street_address else "<MISSING>")
        store.append(city.replace(",",""))
        store.append(state.replace(",",""))
        store.append(zipp.replace(",",""))
        store.append("CA")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("Airport")
        store.append(latitude)
        store.append(longitude)
        store.append("<MISSING>")
        store.append(page_url)
        store.append(website)
        store.append(IATA_code)
        store.append(ICAO_code)
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        # logger.info("data ==="+str(store))
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~```````````")
        yield store


    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
