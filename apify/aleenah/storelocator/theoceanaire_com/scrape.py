import csv
import re
from bs4 import BeautifulSoup
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
    urls=[]
    res=requests.get("https://www.theoceanaire.com/Home.aspx")
    soup = BeautifulSoup(res.text, 'html.parser')
    select=soup.find('select',{'id':'bookLocation'})
    opts=select.find_all('option')
    del opts[0]
    for opt in opts:
        urls.append(opt.text.strip().replace(" ","").replace("D.C.",""))
        ids.append(opt.get("value"))

    for url in urls:
        url="https://www.theoceanaire.com/Locations/"+url+"/Locations.aspx"
        print(url)
        page_url.append(url)
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        div = soup.find('div', {'class': 'contentRight'})
        texs=re.findall(r'(The Oceanaire.*)',div.text,re.DOTALL)[0]
        tex=texs.strip().split("\n")
        if '\r' in tex:
            del tex[tex.index('\r')]

        locs.append(tex[0])
        street.append( tex[1].strip()+" "+tex[2].strip())
        addr=tex[3].split(",")
        print(addr)
        cities.append(addr[0].strip())
        addr=addr[1].strip().split(" ")
        states.append(addr[0])
        zips.append(addr[1])

        p= re.findall(r'([0-9][0-9 \(\)\-]+)',tex[4].strip() )
        if p ==[]:
            phones.append("<MISSING>")
        else:
            phones.append(p[0].strip())

        tim = re.findall(r'(Monday.*pm)',texs,re.DOTALL)[0].replace("\t","").replace("\n"," ").replace("\r","")
        timing.append(tim)

        a = soup.find('div', {'id': "googleMap"}).find("iframe").get("src")
        print(a,"************")
        long.append(re.findall(r'!2d(-?[\d\.]*)',a)[0])
        lat.append(re.findall(r'!3d(-?[\d\.]*)',a)[0])

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.theoceanaire.com")
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
