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
    r = session.get("https://aviewfrommyseat.com/sports", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    type_of_location = {}
    for sport in soup.find("div",{"class":"letter_filter_area paging"}).find_all("a"):
        sport_url = "https://aviewfrommyseat.com"+(sport['href'])
        r1 = session.get(sport_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        
        for venue in soup1.find_all("div",{"class":"level_header"}):
            location = venue.find("p").text.replace("See all","").replace("venues","")
            # print(location_type)
            venue_url = "https://aviewfrommyseat.com/"+venue.find("a")['href']
            r2 = session.get(venue_url, headers=headers)
            soup2 = BeautifulSoup(r2.text, "lxml")
            for link in soup2.find_all("a",{"class":"subtext"}):
                page_url = "https://aviewfrommyseat.com"+link['href']+"about/"
                type_of_location[page_url] = location
    
    loc_type = type_of_location
    r =  requests.get("https://aviewfrommyseat.com/ajax/map.php?jsoncallback=jQuery34107226692616565376_1582850194718&xmin=7.697665325020192&xmax=%2056.745349387957184&ymin=%20-136.35066085170004&ymax=%20-70.96003585170003&show=venues&zoom=4&_=1582850194729", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.text.split("6_1582850194718(")[1].split(');')[0]
    json_data = json.loads(data)
    for mp in json_data:
        # print(mp['name'])
        location_name = (mp['name'].replace(' ',"+"))
        try:
            page_url = "https://aviewfrommyseat.com/venue/"+str(location_name)+"/about/" 
            r =  requests.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "lxml")
            data = soup.find("script",{"type":"application/ld+json"}).text
            json_data = json.loads(data)
            zipp = (json_data['address']['postalCode'])
            phone = json_data['telephone']
            location_type = loc_type[page_url]
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
        store.append(phone.replace("''","<MISSING>") if phone else "<MISSING>")
        store.append(location_type)
        store.append(mp['lat'] if mp['lat'] else "<MISSING>")
        store.append(mp['long'] if mp['long'] else "<MISSING>")
        store.append("<MISSING>")
        store.append(page_url)
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        # if 'store[2]' in addresses :
        #     continue
        # addresses.append(store[2])
        yield store    
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
