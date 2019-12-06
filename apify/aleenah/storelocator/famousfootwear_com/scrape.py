import csv
import requests
import sgzip



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
    key_set=set([])
    zip_codes=sgzip.for_radius(50)
    #headers for linux:
    headers={"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"Accept-Encoding":"gzip, deflate, br",
"Accept-Language":"en-US,en;q=0.5",
 "Connection":"keep-alive",
"Host":"api.famousfootwear.com",
"Upgrade-Insecure-Requests":"1",  
     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0"}
    
    """ headers fro windows:
    {'Sec-Fetch-User': '?1',
'Upgrade-Insecure-Requests': '1',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"}
    """
    for zip in zip_codes:
        print(zip)
        url="https://api.famousfootwear.com/api/store/v1/storesByZip?webStoreId=20000&radius=50&zipCode="+str(zip)+"&json=true"
        res=requests.get(url,headers=headers)
        if 'Stores' in res.json():
            stores=res.json()['Stores']
        else:
            continue
        for store in stores:
            c=store["City"]
            s=store["State"]
            st=store['Address1']+","+store['Address2']
            z=store["Zip"]
            key = c+s+st+z
            #print(key)
            #print(s)
            if key in key_set:
                continue
            else:
                key_set.add(key)
            page_url.append(url)
            street.append(st)
            cities.append(c)
            lat.append(store["Latitude"])
            long.append(store["Longitude"])
            locs.append(store["Name"])
            ids.append(store["Number"])
            phones.append(store["PhoneNumbers"][0]["Value"])
            states.append(s)
            days=store["StoreHoursByDay"]
            if len(days)==14:
                days=days[::2]
            tim=""
            for day in days:
                tim+=day["Day"]+": "+day["OpenTime"]+" - "+day["CloseTime"]+", "

            timing.append(tim)
            zips.append(z)
            #print(locs)


    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.famousfootwear.com/")
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
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)

    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
