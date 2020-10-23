import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('machinefinder_com__ww__en-US__john-deere-dealer-locator')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }
    base_url = "https://www.machinefinder.com/ww/en-US/john-deere-dealer-locator"
    
    r = session.get(base_url,headers=headers)
    soup = BeautifulSoup(r.text,"lxml")

    us_data = soup.find_all("p")[8]
    us_state = us_data.find_all("a")
    for i in us_state:
        state_link = "https://www.machinefinder.com" + i['href']
        state_request = session.get(state_link,headers=headers)
        state_soup = BeautifulSoup(state_request.text,"lxml")
        us_location = state_soup.find_all("div",{"class":"d-listing-info"})

        for citi in us_location:
            location_name = citi.find("div",{"class":"d-listing-name"}).text.strip()
            page_url = "https://www.machinefinder.com" + citi.find("div",{"class":"mf-button-tray"}).find("a")['href']
            
            if len(citi.find_all("div",{"class":"d-listing-style"}))== 3:
                if location_name == "VENEZA EQUIPAMENTOS":
                    street_address = citi.find_all("div",{"class":"d-listing-style"})[0].text + " " + citi.find_all("div",{"class":"d-listing-style"})[1].text
                    temp_city_state_zipp = citi.find_all("div",{"class":"d-listing-style"})[2].text.strip()
                    city = temp_city_state_zipp.split(",")[0]
                    state = temp_city_state_zipp.split(" ")[-2]
                    zipp = temp_city_state_zipp.split(" ")[-1]
                    phone = "<MISSING>"
                elif location_name == "Gonzalez Trading Inc":
                    street_address = "Campo Rico Ave Block C, La Ceramica Industrial park"
                    city = "Carolina"
                    state = "PR"
                    zipp = "00982"
                    phone = "<MISSING>"
                elif "4717 JEFFERIES BOULEVARD" in citi.find_all("div",{"class":"d-listing-style"})[0].text:
                    street_address = "4717 JEFFERIES BOULEVARD"
                    city = "WALTERBORO"
                    state = "SC"
                    zipp = "<MISSING>"
                    phone = "(843) 539-1420"
                else:
                    phone = citi.find_all("div",{"class":"d-listing-style"})[2].text.strip()
                    street_address = citi.find_all("div",{"class":"d-listing-style"})[0].text.strip()
                    temp_city_state_zipp = citi.find_all("div",{"class":"d-listing-style"})[1].text.strip()
                    city = temp_city_state_zipp.split(",")[0]
                    state = temp_city_state_zipp.split(" ")[-2]
                    temp_zipp = temp_city_state_zipp.split(" ")[-1]
                    if len(temp_zipp)==9:
                        zipp = temp_zipp[:5]+"-"+temp_zipp[5:]
                    else:
                        zipp = temp_zipp.replace(".","")

            elif len(citi.find_all("div",{"class":"d-listing-style"}))== 4:
                if location_name == "James River Clearance Center":
                    street_address = "100 Clearance St."
                    city = "Clearance"
                    state = "VA"
                    zipp = "<MISSING>"
                    phone = "804-443-4374"
                else:
                    phone = citi.find_all("div",{"class":"d-listing-style"})[3].text.strip()
                    st2 = citi.find_all("div",{"class":"d-listing-style"})[1].text.strip()
                    st1 = citi.find_all("div",{"class":"d-listing-style"})[0].text.strip()
                    street_address = st1 + " " + st2
                    temp_city_state_zipp = citi.find_all("div",{"class":"d-listing-style"})[2].text.strip()
                    city = temp_city_state_zipp.split(",")[0]
                    state = temp_city_state_zipp.split(" ")[-2]
                    temp_zipp = temp_city_state_zipp.split(" ")[-1]
                    if len(temp_zipp)==9:
                        zipp = temp_zipp[:5]+"-"+temp_zipp[5:]
                    else:
                        zipp = temp_zipp

            elif len(citi.find_all("div",{"class":"d-listing-style"}))== 2:
                if location_name == "TractorOverstock.com":
                    street_address = "<MISSING>"
                    city = "MISSING"
                    state = "IL"
                    zipp = "42066"
                    phone = "(270) 238-7023"
                elif "ROCK ISLAND, IL 61201" in citi.find_all("div",{"class":"d-listing-style"})[0].text:
                    street_address = "<MISSING>"
                    phone = citi.find_all("div",{"class":"d-listing-style"})[1].text.strip()
                    temp_city_state_zipp = citi.find_all("div",{"class":"d-listing-style"})[0].text.strip()
                    city = temp_city_state_zipp.split(",")[0]
                    state = temp_city_state_zipp.split(" ")[-2]
                    zipp = temp_city_state_zipp.split(" ")[-1]
                elif "Dakota Farm Equipment Inventory Clearance Outlet" in location_name:
                    street_address = "<MISSING>"
                    city = "<MISSING>"
                    state = "ND"
                    zipp = "58601"
                    phone = "<MISSING>"
                elif location_name == "C & B Operations Clearance Center":
                    street_address = "<MISSING>"
                    city = "<MISSING>"
                    state = "SD"
                    zipp = "57442"
                    phone = "<MISSING>"
                else:
                    street_address = citi.find_all("div",{"class":"d-listing-style"})[0].text.strip()
                    temp_city_state_zipp = citi.find_all("div",{"class":"d-listing-style"})[1].text.strip()
                    city = temp_city_state_zipp.split(",")[0]
                    state = temp_city_state_zipp.split(" ")[-2]
                    temp_zipp = temp_city_state_zipp.split(" ")[-1]
                    if len(temp_zipp)==9:
                        zipp = temp_zipp[:5]+"-"+temp_zipp[5:]
                    else:
                        zipp = temp_zipp
                        
                    phone = "<MISSING>"
            else:
                continue

            country_code = "US"
            store_number = "<MISSING>"
            location_type = "JOHN DEERE DEALERS"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = "<MISSING>"
            city = city.replace(" - Corporate","").replace("See Ad for Location - ","").replace(" - Sprayer","").replace(" / Joliet","").replace(" - Specials","")
            if location_name == "HCM Australia":
                continue
            else:
                store = []
                store.append(base_url)
                store.append(location_name if location_name else "<MISSING>")
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append(country_code if country_code else "<MISSING>")
                store.append(store_number) 
                store.append(phone if phone else "<MISSING>") 
                store.append(location_type if location_type else "<MISSING>")
                store.append(latitude)
                store.append(longitude)
                store.append(hours_of_operation)
                store.append(page_url)
                if store[2] in addresses:
                        continue
                addresses.append(store[2])
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                # logger.info(store)
                yield store


    ca_data = soup.find_all("p")[9]
    ca_state = ca_data.find_all("a")
    for i in ca_state:
        state_link2 = "https://www.machinefinder.com" + i['href']
        state_request2 = session.get(state_link2,headers=headers)
        state_soup2 = BeautifulSoup(state_request2.text,"lxml")
        ca_location = state_soup2.find_all("div",{"class":"d-listing-info"})

        for citi2 in ca_location:
            location_name = citi2.find("div",{"class":"d-listing-name"}).text
            page_url = "https://www.machinefinder.com" + citi2.find("div",{"class":"mf-button-tray"}).find("a")['href']

            if len(citi2.find_all("div",{"class":"d-listing-style"}))== 3:
                if "www.martindeerline.com" in citi2.find_all("div",{"class":"d-listing-style"})[0].text:
                    street_address = "<MISSING>"
                    temp_city_state_zipp = citi2.find_all("div",{"class":"d-listing-style"})[1].text.replace(" (Turf)","").strip()
                    city = temp_city_state_zipp.split(",")[0]
                    state_zip = temp_city_state_zipp.split(",")[1].split(" ")
                    state = state_zip[1]
                    zipp = "".join(state_zip[2:])
                else:
                    phone = citi2.find_all("div",{"class":"d-listing-style"})[2].text.replace("/","(").strip()
                    street_address = citi2.find_all("div",{"class":"d-listing-style"})[0].text.strip()
                    temp_city_state_zipp = citi2.find_all("div",{"class":"d-listing-style"})[1].text.replace(" (Turf)","").strip()
                    city = temp_city_state_zipp.split(",")[0]
                    state_zip = temp_city_state_zipp.split(",")[1].split(" ")
                    if len(state_zip)==4:
                        state = state_zip[1]
                        zipp = "".join(state_zip[2:])
                    else:
                        try:
                            state = state_zip[1]
                            zipp = state_zip[2]
                        except:
                            state = state_zip[1]
                            zipp = "<MISSING>"


            elif len(citi2.find_all("div",{"class":"d-listing-style"}))== 4:
                phone = citi2.find_all("div",{"class":"d-listing-style"})[3].text.strip()
                street_address = citi2.find_all("div",{"class":"d-listing-style"})[0].text +" "+citi2.find_all("div",{"class":"d-listing-style"})[1].text
                temp_city_state_zipp = citi2.find_all("div",{"class":"d-listing-style"})[2].text.replace(" (Turf)","").strip()
                city = temp_city_state_zipp.split(",")[0]
                state_zip = temp_city_state_zipp.split(",")[1].split(" ")
                if len(state_zip)==4:
                    state = state_zip[1]
                    zipp = "".join(state_zip[2:])
                else:
                    state = state_zip[1]
                    zipp = state_zip[2]
            else:
                street_address = citi2.find_all("div",{"class":"d-listing-style"})[0].text.strip()
                temp_city_state_zipp = citi2.find_all("div",{"class":"d-listing-style"})[1].text.strip()
                city = temp_city_state_zipp.split(",")[0]
                state_zip = temp_city_state_zipp.split(",")[1].split(" ")

                if len(state_zip)==4:
                    state = state_zip[1]
                    zipp = "".join(state_zip[2:])
                else:
                    state = state_zip[1]
                    try:
                        zipp = state_zip[2]
                    except:
                        zipp = "<MISSING>"
                



                phone = "<MISSING>"


            country_code = "CA"
            store_number = "<MISSING>"
            location_type = "JOHN DEERE DEALERS"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = "<MISSING>"

            store = []
            store.append(base_url)
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code if country_code else "<MISSING>")
            store.append(store_number) 
            store.append(phone if phone else "<MISSING>") 
            store.append(location_type if location_type else "<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            if store[2] in addresses:
                    continue
            addresses.append(store[2])
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            # logger.info(store)
            yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
