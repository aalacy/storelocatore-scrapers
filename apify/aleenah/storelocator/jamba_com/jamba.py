import csv
import re
import requests


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

    headers={
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'momentfeed-prod.apigee.net',
        'Origin': 'https://locations.jamba.com',
        'Referer':'https://locations.jamba.com/site-map/US',
        'Sec-Fetch-Mode':'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    }
    res = requests.get("https://momentfeed-prod.apigee.net/api/v2/llp/sitemap?auth_token=PQUBOCBNLKOUIYUP&country=US&multi_account=false",headers=headers,data='auth_token=PQUBOCBNLKOUIYUP&country=US&multi_account=false')
    stores=res.json()['locations']
    key_set=set([])
    for store in stores:
      info=store['store_info']
      so= info['address'].strip()+info['locality'].strip()+info['region'].strip()+info['postcode'].strip()
      if so not in key_set:
        key_set.add(so)

        street.append(info['address'].strip())
        cities.append(info['locality'].strip())
        states.append(info['region'].strip())
        zips.append(info['postcode'].strip())

        page_url.append("https://locations.jamba.com"+store['llp_url'])
    #page_url=list(set(page_url))
    headers = {

        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    }
    for u in page_url:
        url='https://momentfeed-prod.apigee.net/api/llp.json?address='+street[page_url.index(u)].replace(" ","+")+"&auth_token=PQUBOCBNLKOUIYUP&locality="+cities[page_url.index(u)].replace(" ","+")+"&multi_account=false&pageSize=30&region="+states[page_url.index(u)]
        res=requests.get(url,headers=headers)
        #print(url)
        if 'message' in res.json():
            ur=re.findall(r'(.*)#',street[page_url.index(u)].replace(" ","+"))
            if ur!=[]:
                ur=ur[0]
                url = 'https://momentfeed-prod.apigee.net/api/llp.json?address=' + ur + "&auth_token=PQUBOCBNLKOUIYUP&locality=" +cities[page_url.index(u)].replace(" ", "+") + "&multi_account=false&pageSize=30&region=" + states[page_url.index(u)]
                res = requests.get(url, headers=headers)
            if 'message' in res.json():
                print(url)
                locs.append("<MISSING>")
                ids.append("<MISSING>")
                phones.append("<MISSING>")
                timing.append("<MISSING>")
                lat.append("<MISSING>")
                long.append("<MISSING>")
                continue

        info = res.json()[0]['store_info']
        locs.append(info['name'])
        ids.append(info['corporate_id'])
        ph=info['phone']
        if ph=="":
            phones.append("<MISSING>")
        else:
            phones.append(ph)
        tim=info['store_hours']
        if tim=="":
            timing.append("<MISSING>")
        else:
            timing.append(tim)
        lat.append(info['latitude'])
        long.append(info['longitude'])
    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.jamba.com/")
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