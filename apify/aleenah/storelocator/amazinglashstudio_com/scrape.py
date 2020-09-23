import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
import re


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


session = SgRequests()


def fetch_data():
    # Your scraper here

    res = session.get("https://www.amazinglashstudio.com/find-a-studio?searchVal=54000")
    soup = BeautifulSoup(res.text, 'html.parser')
    #print(soup)

    data = re.findall('(studioArray.*)"};', str(soup), re.DOTALL)[0]
    urls = data.split('"};')
    # print(urls)
    ids = re.findall('\["([\d]+)"\]', data)

    all = []
    for yrl in urls:

        url = "https://www.amazinglashstudio.com" + re.findall('(/studios/.*)', yrl)[0]
        print(url)
        if url == 'https://www.amazinglashstudio.com/studios/tx/beaumont/beaumont': #redirects
            continue
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        if 'coming soon' in str(soup).lower():
            print('coming soon')
            continue
        
        jss = soup.find_all('script', {"type": "application/ld+json"})
        if len(jss) == 1:
            jss = jss[0]
        elif len(jss) == 2:
            jss = jss[1]
        else:
            print("lllllllllllllllllllllllllllllllllllllllllllllllll")
        # break
        js = jss.contents
        js = json.loads("".join(js), strict=False)
        addr = js["address"]
        p = js["telephone"]
        if p == "" or p == "TBD":
            p = "<MISSING>"
        lat = js["geo"]["latitude"]
        if lat == "":
            lat = "<MISSING>"
        long = js["geo"]["longitude"]
        if long == "":
            long = "<MISSING>"
        s = addr["streetAddress"].split("[")[0]
        if s == "TBD":
            s = "<MISSING>"
        if "openingHours" in js:
            tim = ' '.join(js["openingHours"])
        else:
            tim = "<MISSING>"
        all.append([
            "https://www.amazinglashstudio.com",
            js["name"],
            s,
            addr["addressLocality"],
            addr["addressRegion"],
            addr["postalCode"].split("-")[0],
            'US',
            ids[urls.index(yrl)],  # store #
            p,  # phone
            js["@type"],  # type
            lat,  # lat
            long,  # long
            tim,  # timing
            url])

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
