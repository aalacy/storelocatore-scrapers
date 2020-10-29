import csv
import re
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('eaglestopstores_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states=[]
    cities = []
    types=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids=[]
    page_url=[]
    headers={'Accept': 'application/json,text/javascript,*/*;q=0.01',
'Accept-Encoding': 'gzip,deflate,br',
'Accept-Language': 'en-US,en;q=0.9',
'Connection': 'keep-alive',
'Content-Length': '114',
'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
'Host': 'eaglestopstores.com',
'Origin': 'https://eaglestopstores.com',
'Referer': 'https://eaglestopstores.com/locations/',
'Sec-Fetch-Mode':'cors',
'Sec-Fetch-Site': 'same-origin',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
'X-Requested-With': 'XMLHttpRequest'}
    res=requests.post("https://eaglestopstores.com/wp-admin/admin-ajax.php",headers=headers,data="action=store_wpress_listener&method=display_list&page_number=1&lat=&lng=&category_id=&max_distance=&nb_display=100")
    stores=res.json()["stores"].split("More information<")
    del stores[-1]
    #logger.info(stores[0])
    for store in stores:
        logger.info(store)
        ll=re.findall(r'<img src=".*center=([\d\.]+),(-?[\d\.]+)&',store)[0]
        lat.append(ll[0])
        long.append(ll[1])
        ids.append(re.findall(r'<a href="https://eaglestopstores.com/c-stores/\?store_id=([0-9]+)"',store)[0])
        locs.append(re.findall(r'class="ygp_sl_stores_list_name">(.*)</a><div class="ygp_sl_stores_list_address',store)[0].strip())
        if "ygp_sl_stores_list_tel" in store:
            phones.append(re.findall(r'class="ygp_sl_stores_list_tel">(.*)</div><div class="ygp_sl_stores_list_more_info_box', store)[0].strip())
        else:
            phones.append("<MISSING>")
        add=re.findall(r'<div class="ygp_sl_stores_list_address">(.*[0-9]{5})</div>',store)
        if add==[]:
            add = re.findall(r'<div class="ygp_sl_stores_list_address">(.*)</div><div class', store)[0].replace("US","")
            if "</div><div class=" in add:
                add = add.split("</div><div class=")[0].strip()
            s=re.findall(r'[A-Z]{2}',add)
            if s==[]:
                s="<MISSING>"
                c="<MISSING>"
                states.append("<MISSING>")
                cities.append("<MISSING>")
            else:
                s=s[-1]
                states.append(s)
                if "," in add:
                    if len(add.split(",")[-2]) <= 2:
                        c = add.split(",")[-2]
                    else:
                        c = add.split(",")[-2].split(" ")[-1]
            street.append(add.replace(s,"").replace(c,"").replace(",","").strip())
            cities.append(c)
            zips.append("<MISSING>")
            continue

        add=add[0].replace("US","")
        if "</div><div class=" in add:
            add=add.split("</div><div class=")[0].strip()

        z= re.findall(r'[0-9]{5}',add)[-1]
        s=re.findall(r'[A-Z]{2}',add)
        add=add.replace(z,"")

        if s != []:
            s=s[-1]
            add=re.findall(r'(.*)[A-Z]{2}',add)[0]
            add=add.replace(s,"")
        else:
            s="<MISSING>"
        if "," in add:
            addr= add.strip().split(",")
            if s=="<MISSING>":
                s=addr[-1].strip()
                if s=="":
                    s="<MISSING>"
                else:
                    add=add.split(s)[0].strip()
            if len(addr[-2]) <= 2:
                c = addr[-2]
            else:
                c = addr[-2].split(" ")[-1]
            add.replace(s, "")
        else:
            add=add.replace(s,"").replace(",","").strip()
            c=add.split(" ")[-1]

        st = add.replace(c,"")

        zips.append(z)
        cities.append(c)
        states.append(s)
        street.append(st.replace(",","").strip())

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://eaglestopstores.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append("<MISSING>")  # timing
        row.append("https://eaglestopstores.com/wp-admin/admin-ajax.php")  # page url
        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
