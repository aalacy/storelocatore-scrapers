import csv
from sgselenium import SgChrome


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
    url = "https://www.corkyskitchenandbakery.com/locations"
    with SgChrome() as driver:
        driver.get(url)
        website = "corkyskitchenandbakery.com"
        typ = "<MISSING>"
        country = "US"
        loc = "<MISSING>"
        store = "<MISSING>"
        hours = "<MISSING>"
        lat = "<MISSING>"
        lng = "<MISSING>"
        text = driver.page_source
        text = str(text).replace("\r", "").replace("\n", "").replace("\t", "")
        if '"@type":"Restaurant","' in text:
            items = text.split('"@type":"Restaurant","')
            for item in items:
                if '"streetAddress":"' in item:
                    add = item.split('"streetAddress":"')[1].split('"')[0]
                    try:
                        phone = item.split('"telephone":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                    try:
                        city = item.split('"addressLocality":"')[1].split('"')[0]
                    except:
                        city = "<MISSING>"
                    try:
                        state = item.split('"addressRegion":"')[1].split('"')[0]
                    except:
                        state = "<MISSING>"
                    try:
                        hours = (
                            item.split('"openingHours":["')[1]
                            .split("]")[0]
                            .replace('","', "; ")
                            .replace('"', "")
                        )
                    except:
                        hours = "<MISSING>"
                    try:
                        zc = item.split('"postalCode":"')[1].split('"')[0]
                    except:
                        zc = "<MISSING>"
                    if "0" not in hours:
                        hours = "<MISSING>"
                    name = city
                    if "0000" in phone:
                        phone = "<MISSING>"
                    if city != "<MISSING>":
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
