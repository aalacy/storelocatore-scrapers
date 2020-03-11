import csv
from bs4 import BeautifulSoup
import json
import requests
from sgrequests import SgRequests
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }
    addresses = []
    r =  requests.get("https://aviewfrommyseat.com/ajax/map.php?jsoncallback=jQuery34107226692616565376_1582850194718&xmin=7.697665325020192&xmax=%2056.745349387957184&ymin=%20-136.35066085170004&ymax=%20-70.96003585170003&show=venues&zoom=4&_=1582850194729", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.text.split("6_1582850194718(")[1].split(');')[0]
    json_data = json.loads(data)
    for mp in json_data:
        location_name = (mp['name'].replace(' ',"+"))
        try:
            zipp1 = ("https://aviewfrommyseat.com/venue/"+str(location_name)+"/about/")
            if 'Theatre' in zipp1:
                location_type='Theatre'
            elif 'Stadium' in zipp1:
                location_type='Stadium'
            else:
                location_type='Teams'        
            r =  requests.get(zipp1, headers=headers)
            soup = BeautifulSoup(r.text, "lxml")
            data = soup.find("script",{"type":"application/ld+json"}).text
            json_data = json.loads(data)
            zipp = (json_data['address']['postalCode'])
            # location_type = json_data['@type']
        except:
            zipp = "<MISSING>"   
        store = []
        if mp['country'] == 'Mexico' or mp['country'] == 'Costa Rica' or mp['country'] =='Nicaragua':
            continue
        store.append("https://aviewfrommyseat.com/")
        store.append(mp['name'] if mp['name'] else "<MISSING>" )
        store.append(mp['address'] if mp['address'] else "<MISSING>")
        store.append(mp['city'] if mp['city'] else "<MISSING>")
        store.append(mp['state'] if mp['state'] else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(mp['country'] if mp['country'] else "<MISSING>")
        store.append(mp['id'] if mp['id'] else "<MISSING>")
        store.append("<MISSING>")
        store.append(location_type)
        store.append(mp['lat'] if mp['lat'] else "<MISSING>")
        store.append(mp['long'] if mp['long'] else "<MISSING>")
        store.append("<MISSING>")
        store.append("https://aviewfrommyseat.com/venue/"+str(location_name)+"/about/")
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        # if 'store[2]' in addresses :
        #     continue
        # addresses.append(store[2])
        yield store    
def scrape():
    data = fetch_data()
    write_output(data)
scrape()