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
    addressesess = []
    base_url = "https://www.avera.org"
    r = session.get("https://www.avera.org/locations/search-results/?sort=13&page=1")
    main_array=[]
    soup = BeautifulSoup(r.text, "lxml")
    option=soup.find("select",{"id":"ce9349e11bda4c59af2fe2dedcc42790_ddl"}).find_all("option")
    for d in option[1:]:
        r5 = session.get("https://www.avera.org/locations/search-results/?termId="+d['value']+"&sort=13&page=1")
        soup5 = BeautifulSoup(r5.text, "lxml")        
        try:
            for number in soup5.find("select",{"class":"SuperShort"}).find_all("option"):
                # print(number.text)l
                r1 = session.get("https://www.avera.org/locations/search-results/?termId="+d['value']+"&sort=13&page="+str(number.text))
                soup1 = BeautifulSoup(r1.text, "lxml")
                for index,url in enumerate(soup1.find("div",{"class":"LocationsList"}).find_all("li")):
                    link = 'https://www.avera.org/locations/'+url.find("a",{"class":"Name"})['href'].replace("..","")
                    if "&id" in link:
                        store_number = link.split("&id=")[-1]
                    else:
                        store_number = "<MISSING>"
                    r2 = session.get(link)
                    soup2 = BeautifulSoup(r2.text, "lxml")
                    location_name=''
                    hp = soup2.find("div",{"class":"LocationProfile"})
                    if  hp != None:
                        links="https://www.avera.org/"+hp['id']+"&skipRedirect=true"
                        # print("new link",links)
                        r3 = session.get(links)
                        soup3 = BeautifulSoup(r3.text, "lxml")
                        # print(str(soup3.find("script",{"type":"text/javascript"})).split('"taxonomy"')[1].split("};")[0])
                        # exit()
                        data = json.loads(soup3.find("script",{"type":"application/ld+json"}).text)
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
                        # print(longitude)
                        if soup2.find("div",{"class":"Hours"}):
                            hours = " ".join(list(soup2.find("div",{"class":"Hours"}).stripped_strings)).replace("Hours of Operation","")
                        else:
                            hours = "<MISSING>"
                    else:
                        # print("~~~~~~~~~~~~~~",link)
                        data = json.loads(soup2.find("script",{"type":"application/ld+json"}).text)
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
                        if soup2.find("div",{"class":"Hours"}):
                            hours = " ".join(list(soup2.find("div",{"class":"Hours"}).stripped_strings)).replace("Hours of Operation","")
                        else:
                            hours = "<MISSING>"
                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append("US")
                store.append(store_number)
                store.append(phone)
                store.append(d.text)
                store.append(latitude)
                store.append(longitude)
                store.append(hours)
                store.append(page_url)
                main_array.append(store)

        except:
            # print(liks1)
           for index,url in enumerate(soup5.find("div",{"class":"LocationsList"}).find_all("li")):
                    link = 'https://www.avera.org/locations/'+url.find("a",{"class":"Name"})['href'].replace("..","")
                    if "&id" in link:
                        store_number = link.split("&id=")[-1]
                    else:
                        store_number = "<MISSING>"
                    r2 = session.get(link)
                    soup2 = BeautifulSoup(r2.text, "lxml")
                    location_name=''
                    hp = soup2.find("div",{"class":"LocationProfile"})
                    if  hp != None:
                        links="https://www.avera.org/"+hp['id']+"&skipRedirect=true"
                        # print("new link",links)
                        r3 = session.get(links)
                        soup3 = BeautifulSoup(r3.text, "lxml")
                        # print(str(soup3.find("script",{"type":"text/javascript"})).split('"taxonomy"')[1].split("};")[0])
                        # exit()
                        data = json.loads(soup3.find("script",{"type":"application/ld+json"}).text)
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
                            longitude= "<MISSING>"
                        page_url = data['url']
                        # print(longitude)
                        if soup2.find("div",{"class":"Hours"}):
                            hours = " ".join(list(soup2.find("div",{"class":"Hours"}).stripped_strings)).replace("Hours of Operation","")
                        else:
                            hours = "<MISSING>"
                    else:
                        # print("~~~~~~~~~~~~~~",link)
                        data = json.loads(soup2.find("script",{"type":"application/ld+json"}).text)
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
                        if soup2.find("div",{"class":"Hours"}):
                            hours = " ".join(list(soup2.find("div",{"class":"Hours"}).stripped_strings)).replace("Hours of Operation","")
                        else:
                            hours = "<MISSING>"
                    store = []
                    store.append(base_url)
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp)
                    store.append("US")
                    store.append(store_number)
                    store.append(phone)
                    store.append(d.text)
                    store.append(latitude)
                    store.append(longitude)
                    store.append(hours)
                    store.append(page_url)
                    main_array.append(store)

                    # print(store)

                    
    for datas in range(len(main_array)):
        if str(main_array[datas][2]+str(main_array[datas][-5])) in addressesess:
                    continue
        addressesess.append(str(main_array[datas][2]+str(main_array[datas][-5])))
        yield main_array[datas]

                # store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                
                # print("data == "+str(store))
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                # yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
