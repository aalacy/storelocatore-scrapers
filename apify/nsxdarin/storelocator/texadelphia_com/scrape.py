import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
    url = "https://texadelphia.com/page-data/sq/d/1906486667.json"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    website = "texadelphia.com"
    typ = "<MISSING>"
    country = "US"
    for line in r.iter_lines(decode_unicode=True):
        if '"id":"' in line:
            items = line.split('"id":"')
            for item in items:
                if '"strapiId":' in item:
                    store = item.split('"strapiId":')[1].split(",")[0]
                    name = item.split('"name":"')[1].split('"')[0]
                    add = item.split('"address":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    zc = item.split('"zip":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    phone = item.split('"phone":"')[1].split('"')[0]
                    lat = item.split('{"lat":')[1].split(",")[0]
                    lng = item.split('"lng":')[1].split("}")[0]
                    loc = "<MISSING>"
                    hours = item.split('"hours1":"')[1].split('"')[0]
                    if 'hours2":"' in item:
                        hours = hours + "; " + item.split('hours2":"')[1].split('"')[0]
                        hours = hours.strip()
                    if 'hours3":"' in item and 'ours3":"Now Open' not in item:
                        hours = hours + "; " + item.split('hours3":"')[1].split('"')[0]
                        hours = hours.strip()
                    yield [
                        website,
                        loc,
                        name,
                        add,
                        city,
                        state,
                        zc,
                        country,
                        store,
                        phone,
                        typ,
                        lat,
                        lng,
                        hours,
                    ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
