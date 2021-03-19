import csv
import json
from lxml import html
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )

        for row in data:
            writer.writerow(row)


def fetch_data():
    out = []
    locator_domain = "https://www.spiceandtea.com"
    api_url = "https://www.spiceandtea.com/where-to-buy"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    block = ''.join(tree.xpath('//script[contains(text(), "jsonLocations")]/text()')).split('jsonLocations: ')[1].replace('\n','').split(',            imageLocations')[0].strip()
    js = json.loads(block)

    for j in js['items']:
        street_address = j.get('address')
        city = j.get('city')
        postal = j.get('zip')
        state = j.get('state')
        phone = j.get('phone') or '<MISSING>'
        if phone.find('COMING') != -1:
            phone = '<MISSING>'
        country_code = 'US'
        store_number = '<MISSING>'
        location_name = j.get('name')
        latitude = j.get('lat')
        longitude = j.get('lng')
        location_type = "<MISSING>"
        page_url = f"https://www.spiceandtea.com/{j.get('website')}"
        hours = j.get('schedule_array')
        tmp = []
        for h in hours:
            days = ''.join(h)
            start = ':'.join(hours.get(days).get('from'))
            if start.count('0') == 4:
                start = 'Closed'
            close = ':'.join(hours.get(days).get('to'))
            if close.count('0') == 4:
                close = 'Closed'
            line = f"{days} {start} - {close}"
            if start == close:
                line = f"{days} Closed"
            tmp.append(line)
        hours_of_operation = ' '.join(tmp) or '<MISSING>'
        if hours_of_operation.count('Closed') == 7:
            hours_of_operation = 'Closed'


        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
