import csv
import re
import requests
import time
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bankatfirst_com')



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
    countries=[]

    #driver.get("https://www.bankatfirst.com/content/first-financial-bank/home/first-financial-locations.html")
    
    headers = {'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en-US,en;q=0.9',
               'Connection': 'keep-alive',
               'Content-Length': '81', 'Content-type': 'application/x-www-form-urlencoded',
               'Host': 'bankatfirst.locatorsearch.com',
               'Origin': 'https://bankatfirst.locatorsearch.com',
               'Referer': 'https://bankatfirst.locatorsearch.com/index.aspx?s=FCS',
               'Sec-Fetch-Mode': 'cors',
               'Sec-Fetch-Site': 'same-origin',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36'}

    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 100.0
    #i=1
    coord = search.next_coord()

    while coord:
        lati=coord[0]
        longi=coord[1]
        r = requests.post("https://bankatfirst.locatorsearch.com/GetItems.aspx", headers=headers,
                      data="lat="+str(lati)+"&lng="+str(longi)+"&searchby=FCS%7C")
    
        data=str(r.content)
        branches=data.split("</marker>")
        del branches[-1]
        result_coords = []
        for b in branches:

            la=re.findall(r'lat="([^"]+)"',b)[0]
            lo=re.findall(r'lng="([^"]+)"',b)[0]
            result_coords.append((la, lo))
            lat.append(la)
            long.append(lo)
            locs.append(re.findall(r'<img alt="(.*)\.gif" src=',b)[0].replace("_logo","")+" "+re.findall(r'\.png"><label><\!\[CDATA\[(.*)\]\]></label>',b)[0])
            try:
                timing.append(re.findall(r'</table><div>(.*)</div>]]></contents></tab><tab><label>',b,re.DOTALL)[0].replace("<br>"," ").replace("\\n"," ").replace("\xe2\x80\x93","").replace("<",""))
                h=1
            except:
                timing.append("<MISSING>")
                h=0
            if h==0:
                t=re.findall(r'<div class="infowindow"><div class="title">.*</div><div>(.*)</div></div>]]></contents></tab>',b)
                if t!=[]:
                    types.append("ATM "+t[0])
                else:
                    types.append("ATM")
                add=re.findall(r'<add2><\!\[CDATA\[(.*)\]\]></add2>',b)[0]
                phones.append("<MISSING>")
            else:
                types.append("Branch center, "+re.findall(r'<div class="infowindow"><div class="title">.*</div><div>(.*)</div></div>]]></contents></tab>',b)[0])
                add=re.findall(r'<add2><\!\[CDATA\[(.*)<br>.*</add2>',b)
                if add==[]:
                    add=re.findall(r'<add2><\!\[CDATA\[(.*)\]\]></add2>',b)
                add=add[0]
                ph=re.findall(r'<add2><.*<br><b>(.*)</b>\]\]></add2>',b)
                if ph!=[]:
                    phones.append(ph[0])
                else:
                    phones.append("<MISSING>")

            street.append(re.findall(r'<add1><\!\[CDATA\[(.*)\]\]></add1>',b)[0])
            addr=add.replace(",,",",").split(",")
            cities.append(addr[0])
            addr= addr[1]
            z=re.findall(r'[0-9]{5}',addr)
            if z ==[]:
                z=re.findall(r'[A-Z][0-9][A-Z] [0-9][A-Z][0-9]',addr)
                if z ==[]:
                    zips.append("<MISSING>")
                    countries.append("US")
                else:
                    zips.append(z[0])
                    countries.append("CA")
            else:
                zips.append(z[0])
                countries.append("US")
                    
            s=re.findall(r' [A-Z]{2}',addr)
            if s !=[]:
                states.append(s[0])
            else:
                states.append("<MISSING>")
        
        if len(branches) == 0:
            logger.info("max distance update")
            search.max_distance_update(50)
        elif len(branches) > 0:
            logger.info("max count update")
            search.max_count_update(result_coords)
        coord = search.next_coord()
        
    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.bankatfirst.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append(countries[i])
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append(types[i])  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append("https://bankatfirst.locatorsearch.com/GetItems.aspx")  # page url

        all.append(row)
    unique_data = [list(x) for x in set(tuple(x) for x in all)]
    return unique_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

