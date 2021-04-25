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
    r = session.get("https://www.bubbagump.com/store-locator/", headers=headers)
    lines = r.iter_lines()
    country = "US"
    website = "bubbagump.com"
    typ = "Restaurant"
    hours = "<MISSING>"
    for line in lines:
        line = str(line.decode("utf-8"))
        if '{"name": "' in line:
            line = line.replace('"categories": [{"name":', "")
            items = line.split('{"name": "')
            for item in items:
                if '"slug": "' in item:
                    store = "<MISSING>"
                    purl = (
                        "https://www.bubbagump.com/location/"
                        + item.split('"slug": "')[1].split('"')[0]
                    )
                    name = item.split('"')[0]
                    lat = item.split('"lat": "')[1].split('"')[0]
                    lng = item.split('"lng": "')[1].split('"')[0]
                    phone = item.split('"phone_number": "')[1].split('"')[0]
                    add = item.split('"street": "')[1].split('"')[0]
                    city = item.split('"city": "')[1].split('"')[0]
                    state = item.split('"state": "')[1].split('"')[0]
                    zc = item.split('"postal_code": "')[1].split('"')[0]
                    hours = (
                        item.split('"hours": "')[1]
                        .split('"')[0]
                        .replace("\\u003cbr/\\u003e", "; ")
                    )
                    hours = hours.replace("\\u003cp\\u003e", "")
                    if "\\u" in hours:
                        hours = hours.split("\\u")[0]
                    if state == "UK":
                        state = "<MISSING>"
                        country = "UK"
                    if state == "AB":
                        country = "CA"
                    name = name.replace("\\u0026", "&")
                    add = add.replace("\\u0026", "&")
                    if (
                        state != "JP"
                        and state != "CNMI"
                        and state != "QA"
                        and state != "CN"
                        and state != "JL"
                        and city != "Bali"
                    ):
                        if "china" not in purl and "cancun" not in purl:
                            yield [
                                website,
                                purl,
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
