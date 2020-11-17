import csv
import gzip

from lxml import html
from sgrequests import SgRequests


def write_output(data):
    with open('data.csv', mode='w', encoding='utf8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        for row in data:
            writer.writerow(row)


def get_urls():
    out = set()
    session = SgRequests()
    r = session.get('https://stores.calvinklein.us/sitemap.xml.gz')
    content = gzip.decompress(r.content)
    tree = html.fromstring(content)
    urls = tree.xpath("//loc/text()")
    for u in urls:
        if u.split('/')[-2].isdigit():
            out.add(u)

    return out


def fetch_data():
    out = []
    url = 'https://stores.calvinklein.us'
    session = SgRequests()
    urls = get_urls()

    s = set()
    for u in urls:
        r = session.get(u)
        tree = html.fromstring(r.text)
        locator_domain = url
        location_name = ''.join(tree.xpath("//h1[@class='heading']/text()")).strip()
        street_address = ''.join(tree.xpath("//meta[@property='business:contact_data:street_address']/@content"))
        city = ''.join(tree.xpath("//meta[@property='business:contact_data:locality']/@content"))
        state = ''.join(tree.xpath("//a[contains(@href, 'maps.apple')]/@href")).split(',')[-2]
        postal = ''.join(tree.xpath("//meta[@property='business:contact_data:postal_code']/@content"))
        country_code = ''.join(tree.xpath("//meta[@property='business:contact_data:country_name']/@content"))
        store_number = u.split('/')[-2]
        phone = ''.join(tree.xpath("//meta[@property='business:contact_data:phone_number']/@content"))
        latitude = ''.join(tree.xpath("//meta[@property='place:location:latitude']/@content"))
        longitude = ''.join(tree.xpath("//meta[@property='place:location:longitude']/@content"))
        page_url = u
        location_type = '<MISSING>'
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        li = tree.xpath("//li[contains(@class,'storeHours-item')]")
        _tmp = []
        i = 0
        for l in li:
            time = ''.join(l.xpath("./span[2]/text()")).strip()
            _tmp.append(f"{days[i]} {time}")
            i += 1

        if _tmp:
            hours_of_operation = ';'.join(_tmp)
        else:
            hours_of_operation = '<MISSING>'

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]

        line = f"{location_name} {street_address} {city} {state} {postal}"
        if line not in s:
            s.add(line)
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
