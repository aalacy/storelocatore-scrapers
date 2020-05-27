import csv
import time
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w',newline='', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    base_url = "https://www.montefiore.org"
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""
    page_url = ""
    addresses = []
    ########################## mmg locations ##################################
    r= session.get("https://www.google.com/maps/d/embed?mid=1KdL2nJazZh47ZXogEriVKB3YLVk&msa=0&ll=40.860555025437755%2C-73.84279832234037&spn=0.005136%2C0.011362&iwloc=0004befb4696e25688410&output=embed&z=17")
    soup = BeautifulSoup(r.text,"lxml")
    script = soup.find(lambda tag: (tag.name == "script") and "var _pageData " in tag.text).text.split("KIEABWLWCFIQ06A469A1")
    for i in script[26:51]:
        location_type = "Montefiore Medical Group"
        store_number = "<MISSING>"
        page_url = "https://www.montefiore.org/mmg-map"
        hours_of_operation = "<MISSING>"
        latitude = i.split("\\n]\\n]\\n,")[0].split("[[[")[1].split(",")[0]
        longitude = i.split("\\n]\\n]\\n,")[0].split("[[[")[1].split(",")[1].split("]")[0]
        location_name = i.split('\\"name\\",')[1].split('\\n,1]')[0].replace('"',"").replace('\\',"").replace("[","").replace("]","").strip()
        address = i.split('\\"description\\",')[1].split('\n,1]')[0].split("\\n")
        
        if len(address) == 7:
            street_address = address[0].split('[\\"')[1].split('\\"]')[0].split(",")[0]
            city= address[0].split('[\\"')[1].split('\\"]')[0].split(",")[1]
            state= address[0].split('[\\"')[1].split('\\"]')[0].split(",")[-1].split()[0]
            zipp = address[0].split('[\\"')[1].split('\\"]')[0].split(",")[-1].split()[-1]
            phone = "<MISSING>"
        elif len(address) == 13:
            street_address = " ".join(address).split("Address: ")[1].split("\\")[0].split(",")[0].replace("Bronx","").strip()
            city ="Bronx"
            state =  " ".join(address).split("Address: ")[1].split("\\")[0].split(",")[1].split()[0]
            zipp = " ".join(address).split("Address: ")[1].split("\\")[0].split(",")[1].split()[-1]
            phone = " ".join(address).split("Phone:")[1].split("\\")[0].replace("CHAM","").strip()
        else:
            try:
                data=int(address[1].strip()[0])
                street_address = address[1].replace("\\","")
                city = address[2].split(",")[0]
                state = address[2].split(",")[-1].replace("\\","").split()[0]
                zipp = address[2].split(",")[-1].replace("\\","").split()[-1]
                phone = " ".join(address).split("Phone:")[1].split("\\")[0].replace(" (Adult Medicine) 718-920-5161 (Pediatrics)","")
            except:
                try:
                    data=int(address[2].strip()[0])
                    street_address = address[2].replace("\\","")
                    city = address[3].split(",")[0]
                    state = address[3].split(",")[-1].replace("\\","").split()[0]
                    zipp = address[3].split(",")[-1].replace("\\","").split()[-1]
                    phone = " ".join(address).split("Phone:")[1].split("\\")[0].replace(" (Adult Medicine) 718-920-5161 (Pediatrics)","")
                except:
                    try:
                        data=int(address[4].strip()[0])
                        street_address = address[4].replace("\\","")
                        city = address[5].split(",")[0]
                        state = address[5].split(",")[-1].replace("\\","").split()[0]
                        zipp = address[5].split(",")[-1].replace("\\","").split()[-1]
                        phone = " ".join(address).split("Phone:")[1].split("\\")[0].replace(" (Adult Medicine) 718-920-5161 (Pediatrics)","")
                    except:
                        phone = " ".join(address).split("Phone:")[1].split("\\")[0].replace(" (Adult Medicine) 718-920-5161 (Pediatrics)","")
                        street_address = " ".join(address).split("Address: ")[1].split("\\")[0].split(",")[0].strip()
                        city =" ".join(address).split("Address: ")[1].split("\\")[0].split(",")[1].strip()
                        state =  " ".join(address).split("Address: ")[1].split("\\")[0].split(",")[-1].split()[0]
                        zipp = " ".join(address).split("Address: ")[1].split("\\")[0].split(",")[-1].split()[-1]
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        if (str(store[1])+str(store[2])) in addresses:
            continue
        addresses.append(str(store[1])+str(store[2]))
        yield store
        # print(store)                
                    
        



        
#################################################################################


   

    r = session.get(base_url,headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for link in soup.find("div",class_="sectionBox grey-box bg-dkblue").find_all("a"):
        if "www" in link["href"]:
            url = link["href"]
            
        elif "/" in link["href"]:
            url = "https://www.montefiore.org"+link["href"]
   
        else:
            url = "https://www.montefiore.org/"+link["href"]
      
        r1 = session.get(url,headers=headers)
        soup1 = BeautifulSoup(r1.text,"lxml")
        try:
            table = soup1.find("div",class_="content").find("table")
            if table:

                for td in table.find_all("td"):
                    try:
                        latitude = td.find("a")["href"].split("sll=")[1].split(",")[0]
                        longitude = td.find("a")["href"].split("sll=")[1].split(",")[1].split("&")[0]
                    except:pass
                    
                    if len(list(td.stripped_strings)) > 1:
                        location_name = list(td.stripped_strings)[0]
                        street_address = list(td.stripped_strings)[1]
                        city = list(td.stripped_strings)[2].split(",")[0]
                        state = list(td.stripped_strings)[2].split(",")[-1].split()[0]
                        zipp = list(td.stripped_strings)[2].split(",")[-1].split()[-1]
                        if "Phone:" in " ".join(list(td.stripped_strings)):
                            phone = list(td.stripped_strings)[-1]
                        else:
                            phone= "<MISSING>"
                        location_type = "Moses Campus"
                        store_number = "<MISSING>"
                        hours_of_operation = "<MISSING>"
                        latitude = "37.0625"
                        longitude = "-95.677068"
                        page_url = url
                    
                        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                            store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                        yield store
                        # print(store)
            else:
                try:
                    url1 = soup1.find("nav",class_="footer-links").find("a",text=re.compile("Locations"))
                    r= session.get("https://www.cham.org"+url1["href"])
                    soup = BeautifulSoup(r.text,"lxml")
                    # print(soup.prettify())
                    loc = list(soup.find_all("div",class_="freeXML")[-1].find("p").stripped_strings)
                    street_address = loc[0]
                    city = loc[1].split(",")[0]
                    state = loc[1].split(",")[1]
                    zipp = loc[1].split(",")[-1].split()[-1]
                    phone = loc[2]
                    location_name = city
                    location_type = "Main campus"
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                    store_number = "<MISSIING>"
                    hours_of_operation = "<MISSING>"
                    page_url = "https://www.cham.org"+url1["href"]
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                            store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                    yield store
                    # print(store)
                    for loc in soup.find("div",class_="freeTxt").find_all("div",class_="column xsm-24 sm-12"):
                        list_loc = list(loc.stripped_strings)
                        if "Phone" in list_loc[-2]:
                            del list_loc[-2]
                        location_name = list_loc[0]
                        phone = list_loc[-1]
                        if len(list_loc) >4:
                            street_address = list_loc[-3]
                            city = list_loc[-2].split(",")[0]
                            state = " ".join(list_loc[-2].split(",")[1].split()[:-1])
                            zipp = list_loc[-2].split(",")[1].split()[-1]
                        elif len(list_loc) ==4 and "NICU" in list_loc[1]:
                            street_address = " ".join(list_loc[2].split(",")[:-2])
                            city = list_loc[2].split(",")[-2]
                            state = list_loc[2].split(",")[-1].split()[0]
                            zipp = list_loc[2].split(",")[-1].split()[-1]
                        else:
                            street_address = list_loc[1]
                            city= list_loc[-2].split(",")[0]
                            state = list_loc[-2].split(",")[1]
                            zipp = "<MISSING>"
                        location_type = "<MISSING>"
                        store_number = "<MISSING>"
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                        hours_of_operation = "<MISSING>"
                        page_url = "https://www.cham.org"+url1["href"]
                        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                            store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                        yield store
                        

                except:
                    if "einstein-campus" in url:
                        r = session.get(url)
                        soup = BeautifulSoup(r.text,"lxml")
                        for loc in soup.find("div",class_="content").find_all("p")[:2]:
                            list_loc = list(loc.stripped_strings)
                               
                            if len(list_loc) == 2:
                                page_url = url
                                city= "<MISSING>"
                                state= "<MISSING>"
                                zipp = "<MISSING>"
                                latitude = "<MISSING>"
                                longitude = "<MISSING>"
                                store_number = "<MISSING>"
                                location_type = "Einstein Campus"
                                location_name = list_loc[0]
                                street_address = list_loc[1]
                                phone = "718-904-2800"
                                hours_of_operation = "24 hours"
                                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                                    store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                                yield store
                                # print(store)
                            else:
                                for i in list_loc[1:]:
                                    page_url = url
                                    city= "<MISSING>"
                                    state= "<MISSING>"
                                    zipp = "<MISSING>"
                                    latitude = "<MISSING>"
                                    longitude = "<MISSING>"
                                    store_number = "<MISSING>"
                                    location_type = "Einstein Campus"
                                    location_name = list_loc[0]
                                    street_address = i
                                    phone = "<MISSING>"
                                    hours_of_operation = "Open Monday through Friday, 7:00 A.M. to 7:00 P.M."
                                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                                    store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                                    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                                    yield store
                                    # print(store)
                    else:
                        r= session.get(url)
                        soup = BeautifulSoup(r.text,"lxml")
                        loc = soup.find("div",{"id":"pagetitlecontainer"})
                        page_url = url
                        store_number = "<MISSING>"
                        if "Wakefield Campus" in loc.text:
                            add = list(soup.find("div",class_="content").find_all("p")[2].stripped_strings)
                            latitude = soup.find("div",class_="content").find_all("p")[3].a["href"].split("sll=")[1].split(",")[0]
                            longitude = soup.find("div",class_="content").find_all("p")[3].a["href"].split("sll=")[1].split(",")[1].split("&")[0]
                            location_name = add[0]
                            location_type = loc.text.strip()
                            street_address = add[1]
                            city = add[2].split(",")[0]
                            state = add[2].split(",")[1].split()[0]
                            zipp = add[2].split(",")[1].split()[-1]
                            phone = add[-1]
                            hours_of_operation = "24-hour"
                        elif "Westchester Square Campus" in loc.text:
                            add = list(soup.find("div",class_="content").find_all("p")[1].stripped_strings)
                            location_name = add[0]
                            location_type = loc.text.strip()
                            street_address = add[1]
                            city = add[2].split(",")[0]
                            state = add[2].split(",")[1].split()[0]
                            zipp = add[2].split(",")[1].split()[-1]
                            phone = add[-1]
                            hours_of_operation = "<MISSING>"
                            latitude = soup.find("div",class_="content").find_all("p")[2].a["href"].split("sll=")[1].split(",")[0]
                            longitude = soup.find("div",class_="content").find_all("p")[2].a["href"].split("sll=")[1].split(",")[1].split("&")[0]
                        else:
                            add = list(soup.find("div",class_="content").find_all("p")[-2].stripped_strings)  
                            location_type = loc.text.strip()
                            location_name= add[0]
                            street_address = add[1]
                            city = add[2].split(",")[0]
                            state = add[2].split(",")[1].split()[0]
                            zipp = add[2].split(",")[1].split()[-1]
                            phone="<MISSING>"
                            hours_of_operation = "<MISSING>"
                            latitude = soup.find("div",class_="content").find("iframe")["src"].split("!2d")[1].split("!2m")[0].split("!3d")[0]
                            longitude = soup.find("div",class_="content").find("iframe")["src"].split("!2d")[1].split("!2m")[0].split("!3d")[1]
                        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                                store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                        yield store
                        # print(store)

        except Exception as e:
            if "burke" in url:
                r= session.get(url+"outpatient/locations")
                soup = BeautifulSoup(r.text,"lxml")
                for ul in soup.find_all("ul",class_="locations-list"):
                    for loc in ul.find_all("li",class_="location-item"):
                        location_name = loc.find("h3").text.strip()
                        add = list(loc.find("div",class_="address-proper").stripped_strings)
                        street_address = " ".join(add[:-1])
                        city = add[-1].split(",")[0]
                        state = add[-1].split(",")[-1].split()[0]
                        zipp = add[-1].split(",")[-1].split()[-1]
                        phone = list(loc.find("div",class_="numbers phone").stripped_strings)[1].strip()
                        try:
                            location_type =loc.find("div",class_="services").text.strip()
                        except:
                            location_type = "<MISSING>"
                        page_url = "https://www.burke.org"+loc.find("h3").find("a")["href"]
                        r_loc = session.get(page_url)
                        soup_loc = BeautifulSoup(r_loc.text,"lxml")
                        try:
                            hours_of_operation = " ".join(list(soup_loc.find("table",class_="location-hours").stripped_strings)).replace("–","-").strip()
                        except:
                            hours_of_operation = "<MISSING>"
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                        store_number = "<MISSING>"
                        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                                store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                        yield store
                        # print(store)
            else:
                r= session.get(url)
                soup = BeautifulSoup(r.text,"lxml")
                try:
                    loc = soup.find("div",class_="footer-area-1").find("div",class_="locations")
                    for li in loc.find("ul").find_all("li"):
                        add = list(li.stripped_strings)
                        if "Directions" in add[-1]:
                            del add[-1]
                        location_name = " ".join(add[:-2])
                        street_address = add[-2]
                        city = add[-1].split(",")[0]
                        state = add[-1].split(",")[-1].split()[0]
                        zipp = add[-1].split(",")[-1].split()[-1]
                        phone = "<MISSING>"
                        hours_of_operation = "<MISSING>"
                        store_number = "<MISSING>"
                        location_type = "Montefiore health system"
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                        page_url = url
                        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                                store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                        if (str(store[1])+str(store[2])) in addresses:
                            continue
                        addresses.append(str(store[1])+str(store[2]))
                        yield store
                        # print(store)
                except:
                    if "montefioreslc" in url:
                        r = session.get(url)
                        soup = BeautifulSoup(r.text,"lxml")
                        loc= soup.find("div",class_="schema-info half")
                        location_name = loc.find("meta",{"itemprop":"name"})["content"]
                        for add in loc.find_all("div",class_="location-info"):
                            street_address = list(add.stripped_strings)[0]
                            city = list(add.stripped_strings)[1]
                            state  = list(add.stripped_strings)[-4]
                            zipp = list(add.stripped_strings)[-3]
                            phone = list(add.stripped_strings)[-1]
                            latitude = "<MISSING>"
                            hours_of_operation = "<MISSING>"
                            store_number = "<MISSING>"
                            location_type = "<MISSING>"
                            latitude = "<MISSING>"
                            longitude = "<MISSING>"
                            page_url = url
                            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                                store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                            yield store
                            #print(store)
                    else:
                        pass

                        

    


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
