import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import html5lib


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    rm = []
    addressess = []
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }
    base_url = "https://bodyalivefitness.com/"
    r = session.get(base_url,headers=header)
    soup = BeautifulSoup(r.text,"html5lib")
    json_data = json.loads(str(soup).split('<script type="application/ld+json">')[1].split("</script>")[0].strip())['location']
    for val in json_data:
        location_name = val['name']
        page_url = val['url']
        street_address = val['address']['streetAddress']
        city = val['address']['addressLocality']
        state = val['address']['addressRegion']
        zipp = val['address']['postalCode']
        phone = val['telephone']
        lat = val['geo']['latitude']
        lng = val['geo']['longitude']
        hours_of_operation = ", ".join(val['openingHours'])
        rm.append(page_url)
        store = []
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append("US")
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append("Body Alive Fitness")
        store.append(lat if lat else '<MISSING>')
        store.append(lng if lng else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url)
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store

    menu = soup.find("ul",{"id":"top-menu"}).find("ul",{"class":"sub-menu"})
    for location in menu.find_all("li",{"id":re.compile("menu-item-")})[1:]:
        link = location.find("a")["href"]
        if link in rm:
            continue
        location_request = session.get(link,headers=header)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        location_name = location_soup.find("h2").find("strong").text
        try:
            addr =list(location_soup.find_all("div",{"class":"et_pb_text_inner"})[-1].stripped_strings)
            street_address = addr[0]
            city = addr[1].split(",")[0]
            state = addr[1].split(",")[1].strip().split(" ")[0]
            zipp = addr[1].split(",")[1].strip().split(" ")[1]
            phone = addr[2]
        except IndexError:
            addr = list(location_soup.find_all("div",{"class":"et_pb_text_inner"})[1].stripped_strings)
            street_address = addr[0]
            city = addr[1].split(",")[0]
            state = addr[1].split(",")[1].strip().split(" ")[0]
            zipp = addr[1].split(",")[1].strip().split(" ")[1]
            phone = "<MISSING>"
        map_url = location_soup.find("iframe")['src'].split("2d")[1].split("!1")[0].replace("!2m3","").replace("!3m2","").split("!3d")
        lat = map_url[1]
        lng = map_url[0]
        hours_of_operation = "<MISSING>"
        page_url = link
        store = []
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append("US")
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append("Body Alive Fitness")
        store.append(lat if lat else '<MISSING>')
        store.append(lng if lng else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url)
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
