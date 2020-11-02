import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()

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
    return_main_object = []
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Connection': 'keep-alive',
    }
    base_url = "https://www.wyndhamhotels.com"
    r1 = session.get("https://www.wyndhamhotels.com/BWSServices/services/search/properties?recordsPerPage=15000&pageNumber=1&brandId=ALL&countryCode=US%2CCA%2CMX", headers= headers).json()
    for i in r1["countries"]:
        for j in i['states']:
            state = (j["stateName"].lower().replace(" ","-"))
            for k in j['cities']:
                city = (k["cityName"].lower().replace(" ","-"))
                for h in k["propertyList"]:
                    brand = (h["brand"].replace("Microtel Inn","microtel").replace("Wyndham","wyndham-garden").replace("Vacation Ownership","wyndham-vacations").replace("Hawthorn","hawthorn-extended-stay").replace("Baymont Inns","baymont").replace("Wingate Hotels","wingate").lower().replace("super8","super-8").replace(" ","-"))
                    unique_url = (h["uniqueUrl"]) 
                    url = "https://www.wyndhamhotels.com/en-ca/"+str(brand)+"/"+str(city)+"-"+str(state)+"/"+str(unique_url)+"/overview"
                    try:
                        r1 = session.get(url, headers=headers,  allow_redirects=False)
                    except:
                        pass
                    soup1= BeautifulSoup(r1.text,"lxml")
                    b = soup1.find("script",{"type":"application/ld+json"})
                    if b != [] and b != None:
                        try:
                            h  = json.loads(b.text)  
                        except:
                            pass
                        if 'name' in h :
                            location_name = (h['name'])
                        else:
                            location_name = "<MISSING>"
                        if "Baymont " in location_name:
                            location_name = location_name
                        else:
                            continue
                        if "address" in h:
                            if "streetAddress" in h['address']:
                                street_address = h['address']["streetAddress"]
                            else:
                                street_address = "<MISSING>"
                        else:
                            street_address = "<MISSING>"
                        if "address" in h:
                            if "addressLocality" in h['address']:
                                city = h['address']["addressLocality"]
                            else:
                                city = "<MISSING>"
                        else:
                            city = "<MISSING>"
                        if "address" in h:
                            if "addressRegion" in h['address']:
                                state = h['address']["addressRegion"]
                            else:
                                state = "<MISSING>"
                        else:
                            state = "<MISSING>"
                            # state = h['address']["addressRegion"]
                        if "address" in h:
                            if "postalCode" in h['address']:
                                zipp = h['address']["postalCode"]
                            else:
                                zipp = "<MISSING>"
                            ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp))
                            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp))
                            if ca_zip_list:
                                zipp = ca_zip_list[-1]
                                country_code = "CA"
                            if us_zip_list:
                                zipp = us_zip_list[-1]
                                country_code = "US"
                            if len(zipp) == 6 or len(zipp) == 7:
                                country_code = "CA"
                            else:
                                country_code = "US"
                        else:
                            zipp = "<MISSING>"

                        if "geo" in h:
                            if "latitude" in h['geo']:
                                latitude = h['geo']["latitude"]
                            else:
                                latitude = "<MISSING>"
                        else:
                            latitude = "<MISSING>"

                        if "geo" in h:
                            if "longitude" in h['geo']:
                                longitude = h['geo']["longitude"]
                            else:
                                longitude = "<MISSING>"
                        else:
                            longitude = "<MISSING>"

                        # latitude = h['geo']["latitude"]
                        # longitude = h['geo']["longitude"]
                        phone = h['telephone']              
                        store = []
                        store.append("https://www.baymontinns.com")
                        store.append(location_name if location_name else "<MISSING>") 
                        store.append(street_address if street_address else "<MISSING>")
                        store.append(city if city else "<MISSING>")
                        store.append(state if state else "<MISSING>")
                        store.append(zipp if zipp else "<MISSING>")
                        store.append(country_code)
                        store.append("<MISSING>") 
                        store.append(phone if phone else "<MISSING>" )
                        store.append("<MISSING>")
                        store.append( latitude if latitude else "<MISSING>")
                        store.append( longitude if longitude else "<MISSING>")
                        store.append("<MISSING>")
                        store.append(url)
                        if store[2] in addresses :
                            continue
                        addresses.append(store[2])
                        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
