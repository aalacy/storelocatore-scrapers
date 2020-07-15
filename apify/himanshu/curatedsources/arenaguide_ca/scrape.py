import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import usaddress
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
    addresses = []
    base_url = "http://arenaguide.ca"    

    payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"action\"\r\n\r\nget-items:getHeaderMapMarkers\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"type\"\r\n\r\nheaderMap\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"pageType\"\r\n\r\nsearch\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"postType\"\r\n\r\nait-item\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[s]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[error]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[m]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[p]\"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[post_parent]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[subpost]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[subpost_id]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[attachment]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[attachment_id]\"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[name]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[pagename]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[page_id]\"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[second]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[minute]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[hour]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[day]\"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[monthnum]\"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[year]\"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[w]\"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[category_name]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[tag]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[cat]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[tag_id]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[author]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[author_name]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[feed]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[tb]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[paged]\"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[meta_key]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[meta_value]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[preview]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[sentence]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[title]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[fields]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[menu_order]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[embed]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[posts_per_page]\"\r\n\r\n20\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[post_type]\"\r\n\r\nait-item\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[suppress_filters]\"\r\n\r\nfalse\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[meta_query][featured_clause][key]\"\r\n\r\n_ait-item_item-featured\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[meta_query][featured_clause][compare]\"\r\n\r\nEXISTS\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[orderby][featured_clause]\"\r\n\r\nDESC\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[orderby][title]\"\r\n\r\nASC\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[ignore_sticky_posts]\"\r\n\r\nfalse\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[cache_results]\"\r\n\r\ntrue\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[update_post_term_cache]\"\r\n\r\ntrue\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[lazy_load_term_meta]\"\r\n\r\ntrue\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[update_post_meta_cache]\"\r\n\r\ntrue\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[nopaging]\"\r\n\r\nfalse\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[comments_per_page]\"\r\n\r\n50\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[no_found_rows]\"\r\n\r\nfalse\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"globalQueryVars[order]\"\r\n\r\nDESC\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"query-data[search-filters][selectedCount]\"\r\n\r\n20\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"query-data[search-filters][selectedOrderBy]\"\r\n\r\ntitle\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"query-data[search-filters][selectedOrder]\"\r\n\r\nASC\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"query-data[advanced-filters]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"query-data[search-params][s]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"query-data[search-params][category]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"query-data[search-params][location-address]\"\r\n\r\n80261\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"query-data[search-params][lat]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"query-data[search-params][lon]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"query-data[search-params][runits]\"\r\n\r\nkm\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"query-data[search-params][rad]\"\r\n\r\n100\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"query-data[search-params][a]\"\r\n\r\ntrue\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"query-data[ajax][limit]\"\r\n\r\n5000\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"query-data[ajax][offset]\"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"lang\"\r\n\r\nen\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"is_post_preview\"\r\n\r\nfalse\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"search-params[s]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"search-params[category]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"search-params[location-address]\"\r\n\r\n80261\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"search-params[lat]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"search-params[lon]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"search-params[runits]\"\r\n\r\nkm\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"search-params[rad]\"\r\n\r\n100\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"search-params[a]\"\r\n\r\ntrue\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"ignorePagination\"\r\n\r\ntrue\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"enableTel\"\r\n\r\ntrue\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'cache-control': "no-cache",
        'postman-token': "7acdbaf7-3eba-6142-3f10-b97f02cb29ec"
        }

    response = session.post("https://arena-guide.com/wp-admin/admin-ajax.php", data=payload, headers=headers).json()['data']['raw_data']['markers']
    
    for name in response:
        location_name = name['title']
        lat = name['lat']
        lng = name['lng']
        soup = BeautifulSoup(name['context'],"lxml")
    
        raw_address = soup.find("span",{"class":"item-address"}).text
        ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(raw_address))
        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(raw_address))
        
        country_code = ''
        zipp = ''
        if ca_zip_list:
            zipp = ca_zip_list[-1]
            country_code = "CA"

        elif us_zip_list:
            zipp = us_zip_list[-1]
            country_code = "US"
        address = usaddress.parse(raw_address.replace(zipp,"").replace(", Canada","").replace("Canada,","").replace("Canada","").replace(", USA","").replace("USA",""))

        city = []
        state = []
        street_address = []
        for info in address:

            if 'PlaceName' in info:
                city.append(info[0])

            if "StateName" in info:
                state.append(info[0])
            
            if "AddressNumber" in info:
                street_address.append(info[0])
            if "StreetNamePreType" in info:
                street_address.append(info[0])
            if "StreetName" in info:
                street_address.append(info[0])
            if "StreetNamePostType" in info:
                street_address.append(info[0])
            if "StreetNamePostDirectional" in info:
                street_address.append(info[0])
            if "OccupancyType" in info:
                street_address.append(info[0])
            if "OccupancyIdentifier" in info:
                street_address.append(info[0])
        
        street_address = " ".join(street_address).replace(",","").replace("Ave.","Avenue")
        city = " ".join(city).replace(",","")
        state = " ".join(state).replace(",","").replace("PEI","PE").replace("Wisconsin","WI").replace("BC BC","BC").replace("Champlin","").replace("La QC","QC")

        if "T-126" in street_address:
            street_address = "T-126, 100 Ramillies Rd."
            city = "Angus"

        if "604 rue 9e " in street_address:
            street_address = "604 rue 9e (boul. Desrochers)"
            city = "La Pocatière"
        page_url = soup.find("a")['href']
        try:
            phone = soup.find("a",{"class":"phone"}).text.split("ext")[0].split("EXT")[0].split("x")[0].split("#")[0].split(",")[0].replace("(Main)","").replace("E","").replace("CITY","").split("/")[0].replace("(Arena)","").split("X")[0].replace("819 819-797-7110","819-797-7110").replace("310-398-57819","310-398-5781").strip()
        except:
            phone = "<MISSING>"  



        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append("<MISSING>") 
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        store.append(page_url)

        if store[2] in addresses:
            continue
        addresses.append(store[2])

        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store

                
def scrape():
    data = fetch_data()
    write_output(data)

scrape()

