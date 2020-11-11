import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    addressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.thebeerstore.ca/"
    locator_domain = "https://www.thebeerstore.ca/stores/"
    r = session.get(locator_domain,headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for loc in soup.find("div",{"class":"new_all_stores_wrap"}).find_all("a",{"class":"site_default_btn"}):
        page_url = loc['href']
        r1 = session.get(page_url,headers=headers)
        soup1= BeautifulSoup(r1.text,'lxml')
        location_name = soup1.find("div",{"class":"top_sectionDiv"}).find("h2").text.strip()
        store_number = soup1.find("div",{"class":"top_sectionDiv"}).find("p").text.replace("Store #","").strip()
        addr = soup1.find("div",{"class":"col-md-3 store-section-inc"}).find("a").text.split(",")
        city = location_name.title().replace("Mobile store # 1","Mississauga").replace("Barrys bay","Barry's Bay").replace("BarryS Bay","Barry's Bay").replace("Yonge St. N.","Gwillimbury")
        citylst = ['Burlington','Mississauga','Aurora','Barrie','Belleville','Brampton','Brantford','Burlington','Cambridge','Chatham','Coniston','Cornwall','East York','Etobicoke','Fonthill','Gloucester',
                   'Guelph','Hamilton','Hanover','Kanata','Kingston','Kitchener','LaSalle','Lively','London','Markham','Midland','Newmarket','Niagara Falls','Nelville','North Bay','North York','Oakville',
                   'Orillia','Orleans','Oshawa','Ottawa','Pembroke','Peterborough','Pickering','Richmond Hill','Sarnia','Marie','Scarborough','Shelburne','Catharines','Stittsville','Stoney Creek','Sudbury',
                   'Thunder Bay','Timmins','Toronto','Vaughan','Waterloo','Whitby','Windsor','Woodbridge','Woodstock','York']
        for i in citylst:
            if i in soup1.find("div",{"class":"col-md-3 store-section-inc"}).find("a").text:
                city = i
        street_address = addr[0].replace(city,"").strip()
        zipp = addr[-1]
        phone = soup1.find("a",{"class":"tel-hl-tbs"}).text.replace("Warning:  preg_match() expects parameter 2 to be string, array given in /nas/content/live/tbsecomp/wp-content/themes/Beer-Store/functions.php on line 1306","").strip()
        map_url = soup1.find("div",{"class":"store_map"}).find("img")['src'].split("|")[1].split("&")[0].split(",")
        latitude = map_url[0]
        longitude = map_url[1]
        hours_of_operation = " ".join(list(soup1.find_all("div",{"class":"rite_col"})[-1].stripped_strings)).replace("\n","").replace("                                           ","")
        store = []
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append('<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append("CA")
        store.append(store_number)
        store.append(phone if phone else '<MISSING>')
        store.append("The Beer Store")
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation.replace("Store Hours Day Hours ",'') if hours_of_operation else '<MISSING>')
        store.append(page_url)
        store = [x.replace("—","-") if type(x) == str else x for x in store] 
        store = [x.strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
