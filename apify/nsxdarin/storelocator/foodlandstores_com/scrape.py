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
    url = "https://api.freshop.com/1/stores?app_key=foodland_unfi&has_address=true&is_selectable=true&limit=-1&token=efc0cec6c6d24a5305bdfd23798791f7"
    r = session.get(url, headers=headers)
    website = "foodlandstores.com"
    country = "US"
    typ = "<MISSING>"
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"id":"' in line:
            items = line.split('{"id":"')
            for item in items:
                if '"name":"' in item:
                    store = item.split('"')[0]
                    name = item.split('"name":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(",")[0]
                    lng = item.split('"longitude":')[1].split(",")[0]
                    loc = item.split('"url":"')[1].split('"')[0]
                    try:
                        add = item.split('"address_0":"')[1].split('"')[0]
                    except:
                        add = ""
                    add = add + " " + item.split('"address_1":"')[1].split('"')[0]
                    add = add.strip()
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"postal_code":"')[1].split('"')[0]
                    hours = item.split('"hours_md":"')[1].split('"')[0]
                    phone = item.split('"phone_md":"')[1].split('"')[0]
                    hours = hours.replace("Hours: ", "")
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
