import csv
import re
import sgzip
import requests
from bs4 import BeautifulSoup


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

    zip_codes=sgzip.for_radius(50)

    key_set = set([])
    for zip in zip_codes:
        #zip=44140
        print(zip)
        url = "https://www.northwest.bank/locations?zip="+str(zip)+"&type=both&distance=50"
        res=requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        try:
            lis = soup.find_all('div', {'class': 'branches'})[0].find_all("li")
            for li in lis:
                addr = li.find('p', {'class': 'address'}).text.strip().split("\n")
                #print(addr)
                st = addr[0].strip()
                c=addr[1].replace(",", "").strip()
                addr = re.sub("[ ]+", " ", addr[2].strip()).split(" ")
                s=addr[0]
                z=addr[1]
                key = st+s+z+c
                if key not in key_set:
                    print("key")
                    key_set.add(key)
                    street.append(st)
                    states.append(s)
                    zips.append(z)
                    cities.append(c)
                    page_url.append(url)
                    l= li.find("h4").text
                    locs.append(l.strip())
                    #print("here1")
                    info = li.find('div', {'class': 'info'})
                    if "ATM" in l:
                        types.append("ATM")
                        timing.append(info.find('p').text.replace("\n"," ").strip())
                    else:
                        t="Branch"
                        tim= info.find('p').text.replace("\n"," ").strip()
                        if "ATM" in tim:
                            t="Branch+ATM"
                        types.append(t)
                        timing.append(re.findall(r'(.*pm)',tim)[0])
                    #print("here2")
                    coord = info.find('a').get('href')
                    lat.append(re.findall(r'/%40(-?[\d\.]*)%2C[-?\d\.]*%2C',coord)[0])
                    long.append(re.findall(r'/%40[-?\d\.]*%2C(-?[\d\.]*)%2C',coord)[0])
                    #print("here3")
                    ph=li.find_all('a', {'class': 'phone'})
                    if ph==[]:
                        phones.append("<MISSING>")
                    else:
                        phones.append(ph[0].text.strip())
                    but=li.find_all('button', {'class': 'select-branch'})
                    if but!=[]:
                        ids.append(but[0].get('data-nid'))
                    else:
                        ids.append("<MISSING>")
                    print("cool!")
        except:
            print("pass")
            continue


    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.northwest.bank")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append(types[i])  # type
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

