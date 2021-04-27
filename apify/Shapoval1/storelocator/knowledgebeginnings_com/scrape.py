import csv

from concurrent import futures
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


def get_ids():
    ids = []
    session = SgRequests()
    r = session.get('https://www.kindercare.com/sitemap.xml')
    tree = html.fromstring(r.content)
    urls = tree.xpath("//loc[contains(text(), '/our-centers/')]/text()")
    for u in urls:
        _id = u.split('/')[-1]
        if _id.isdigit():
            ids.append(_id)

    return ids


def get_data(store_number):
    locator_domain = 'https://www.knowledgebeginnings.com/'
    page_url = f'https://www.knowledgebeginnings.com/our-centers/center-details/{store_number}/'

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    try:
        line = tree.xpath("//div[@class='address']/p/b/text()")
    except IndexError:
        return
    line = list(filter(None, [l.strip() for l in line]))
    print(page_url, ':', line)
    try:
        location_name = line.pop(0)
    except IndexError:
        location_name = '<MISSING>'
    street_address = ', '.join(line[:-1])
    line = line[-1]
    city = line.split(',')[0].strip()
    line = line.split(',')[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = 'US'
    phone = ''.join(tree.xpath("//p[contains(text(), 'Phone')]/text()")).replace('Phone:', '').strip() or '<MISSING>'
    if 'Fax' in phone:
        phone = phone.split('Fax')[0].strip()

    try:
        text = ''.join(tree.xpath("//script[contains(text(), 'google.maps.LatLng')]/text()"))
        latitude, longitude = eval(text.split('point = new google.maps.LatLng')[1].split(';')[0])
    except:
        latitude, longitude = '<MISSING>', '<MISSING>'
    location_type = '<MISSING>'

    hours_of_operation = ''.join(tree.xpath("//li[contains(text(), 'Open: ')]/text()")).replace('Open:', '').strip() or '<MISSING>'

    row = [locator_domain, page_url, location_name, street_address, city, state, postal,
           country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]

    return row


def fetch_data():
    out = []
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, _id): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
