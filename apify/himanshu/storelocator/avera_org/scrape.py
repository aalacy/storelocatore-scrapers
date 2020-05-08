import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = locator_domain = "https://www.avera.org"
    addresses=[]
    country_code = "US"
    r = session.get("https://www.avera.org/locations/search-results/?sort=13&page=1")
    soup = BeautifulSoup(r.text, "lxml")
    option=soup.find("select",{"id":"ce9349e11bda4c59af2fe2dedcc42790_ddl"}).find_all("option")
    
    for d in option[1:]:
        
        location_type = d.text
        # print(location_type)
        r1 = session.get("https://www.avera.org/locations/search-results/?termId="+d["value"]+"&zipCode=&sort=13&page=1")
        soup1 = BeautifulSoup(r1.text, "lxml")        
        if soup1.find("select",{"class":"SuperShort"}): 
            for number in soup1.find("select",{"class":"SuperShort"}).find_all("option"):
                # loc_list.append(d.text)
                url1 = "https://www.avera.org/locations/search-results/?termId="+d['value']+"&zipCode=&sort=13&page="+str(number.text)
                r2 = session.get(url1)
                soup2 = BeautifulSoup(r2.text, "lxml")
                for index,url in enumerate(soup2.find("div",{"class":"LocationsList"}).find_all("li")):
                    link = 'https://www.avera.org/locations/'+url.find("a",{"class":"Name"})['href'].replace("..","")
                    if "&id" in link:
                        store_number = link.split("&id=")[-1]
                    else:
                        store_number = "<MISSING>"
                    r3 = session.get(link)
                    soup3 = BeautifulSoup(r3.text, "lxml")
                    hp = soup3.find("div",{"class":"LocationProfile"})
                    if  hp != None:
                        links="https://www.avera.org/"+hp['id']+"&skipRedirect=true"
                        # print("new link===",links)
                        r4 = session.get(links)
                        soup4 = BeautifulSoup(r4.text, "lxml")
                        data = json.loads(soup4.find("script",{"type":"application/ld+json"}).text)
                        location_name = data['name']
                        street_address = data['address']['streetAddress'].split("Suite")[0].replace(",","").split("Ste")[0].replace("Second Floor","").replace("3rd Floor","").replace("2nd Floor","").replace("4th Floor - Plaza 2","")
                        city = data['address']['addressLocality']
                        state = data['address']['addressRegion']
                        zipp = data['address']['postalCode']
                        phone = data['telephone']
                        try:
                            latitude = data['geo']['latitude']
                            longitude = data['geo']['longitude']
                        except:
                            latitude="<MISSING>"
                            longitude="<MISSING>"
                        page_url = data['url']
                        if soup4.find("div",{"class":"Hours"}):
                            hours = " ".join(list(soup4.find("div",{"class":"Hours"}).stripped_strings)).replace("Hours of Operation","")
                        else:
                            hours = "<MISSING>"
                    

                    else:
                        data = json.loads(soup3.find("script",{"type":"application/ld+json"}).text)
                        # print(data)
                        location_name = data['name']
                        street_address = data['address']['streetAddress'].split("Suite")[0].replace(",","").split("Ste")[0].replace("Second Floor","").replace("3rd Floor","").replace("2nd Floor","").replace("4th Floor - Plaza 2","")
                        city = data['address']['addressLocality']
                        state = data['address']['addressRegion']
                        zipp = data['address']['postalCode']
                        phone = data['telephone']
                        try:
                            latitude = data['geo']['latitude']
                            longitude = data['geo']['longitude']
                        except:
                            latitude="<MISSING>"
                            longitude="<MISSING>"
                        page_url = data['url']
                        if soup3.find("div",{"id":"OfficeHourComment"}):
                            hours = " ".join(list(soup3.find("div",{"id":"OfficeHourComment"}).stripped_strings)).replace("Avera QuickLabs Hours","")
                        else:
                            hours = "<MISSING>"
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                            store_number, phone, location_type, latitude, longitude, hours,page_url]
                    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                    duplicate =str(store[1])+" "+str(store[2])+" "+str(store[3])+" "+str(store[4])+" "+str(store[5])+" "+str(store[6])+" "+str(store[7])+" "+str(store[8])+" "+str(store[9])+" "+str(store[10])+" "+str(store[11])+" "+str(store[12])+" "+str(store[13])
                    if str(duplicate)  in addresses:
                        continue
                    addresses.append(str(duplicate))
                    #print("data = " + str(store))
                    #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    yield store
                                        
        else:
            url1 = "https://www.avera.org/locations/search-results/?termId="+d["value"]+"&zipCode=&sort=13&page=1"
            r2 = session.get(url1)
            soup2 = BeautifulSoup(r2.text, "lxml")
            for index,url in enumerate(soup2.find("div",{"class":"LocationsList"}).find_all("li")):
                link = 'https://www.avera.org/locations/'+url.find("a",{"class":"Name"})['href'].replace("..","")
                if "&id" in link:
                    store_number = link.split("&id=")[-1]
                else:
                    store_number = "<MISSING>"
                r3 = session.get(link)
                soup3 = BeautifulSoup(r3.text, "lxml")
                hp = soup3.find("div",{"class":"LocationProfile"})
                if  hp != None:
                    links="https://www.avera.org/"+hp['id']+"&skipRedirect=true"
                    # print("new link===",links)
                    r4 = session.get(links)
                    soup4 = BeautifulSoup(r4.text, "lxml")
                    data = json.loads(soup4.find("script",{"type":"application/ld+json"}).text)
                    location_name = data['name']
                    street_address = data['address']['streetAddress'].split("Suite")[0].replace(",","").split("Ste")[0].replace("Second Floor","").replace("3rd Floor","").replace("2nd Floor","").replace("4th Floor - Plaza 2","")
                    city = data['address']['addressLocality']
                    state = data['address']['addressRegion']
                    zipp = data['address']['postalCode']
                    phone = data['telephone']
                    try:
                        latitude = data['geo']['latitude']
                        longitude = data['geo']['longitude']
                    except:
                        latitude="<MISSING>"
                        longitude="<MISSING>"
                    page_url = data['url']
                    if soup4.find("div",{"class":"Hours"}):
                        hours = " ".join(list(soup4.find("div",{"class":"Hours"}).stripped_strings)).replace("Hours of Operation","")
                    else:
                        hours = "<MISSING>"
                

                else:
                    data = json.loads(soup3.find("script",{"type":"application/ld+json"}).text)
                    # print(data)
                    location_name = data['name']
                    street_address = data['address']['streetAddress'].split("Suite")[0].replace(",","").split("Ste")[0].replace("Second Floor","").replace("3rd Floor","").replace("2nd Floor","").replace("4th Floor - Plaza 2","")
                    city = data['address']['addressLocality']
                    state = data['address']['addressRegion']
                    zipp = data['address']['postalCode']
                    phone = data['telephone']
                    try:
                        latitude = data['geo']['latitude']
                        longitude = data['geo']['longitude']
                    except:
                        latitude="<MISSING>"
                        longitude="<MISSING>"
                    page_url = data['url']
                    if soup3.find("div",{"id":"OfficeHourComment"}):
                        hours = " ".join(list(soup3.find("div",{"id":"OfficeHourComment"}).stripped_strings)).replace("Avera QuickLabs Hours","")
                    else:
                        hours = "<MISSING>"
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                            store_number, phone, location_type, latitude, longitude, hours,page_url]
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                duplicate =str(store[1])+" "+str(store[2])+" "+str(store[3])+" "+str(store[4])+" "+str(store[5])+" "+str(store[6])+" "+str(store[7])+" "+str(store[8])+" "+str(store[9])+" "+str(store[10])+" "+str(store[11])+" "+str(store[12])+" "+str(store[13])
                if str(duplicate)  in addresses:
                    continue
                addresses.append(str(duplicate))
                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store       




def scrape():
    data = fetch_data()
    write_output(data)

scrape()
