import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("homesense_co_uk")


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
    locs = []
    url = "https://www.homesense.com/find-a-store"
    r = session.get(url, headers=headers)
    website = "homesense.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "\\u0022\\/stores\\/" in line:
            items = line.split("\\u0022\\/stores\\/")
            for item in items:
                if "View store info" in item:
                    locs.append(
                        "https://www.homesense.com/stores/" + item.split("\\")[0]
                    )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = loc.rsplit("/", 1)[1].replace("%20", " ")
        state = "<MISSING>"
        zc = ""
        store = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2 and name == "":
                name = line2.split("<title>")[1].split("<")[0]
                if "|" in name:
                    name = name.split("|")[0].strip()
            if hours == "" and '<span itemprop="openingHours" datetime="">' in line2:
                hours = line2.split('<span itemprop="openingHours" datetime="">')[
                    1
                ].split("<")[0]
            if '"latitude":"' in line2:
                lat = line2.split('"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
            if add == "" and 'itemprop="streetAddress">' in line2:
                add = line2.split('itemprop="streetAddress">')[1].split("<")[0]
            if 'itemprop="addressLocality">' in line2 and city == "":
                add = (
                    add
                    + " "
                    + line2.split('itemprop="addressLocality">')[1].split("<")[0]
                )
            if 'itemprop="zipCode">' in line2 and zc == "":
                zc = line2.split('itemprop="zipCode">')[1].split("<")[0]
            if store == "" and 'data-store-id="' in line2:
                store = line2.split('data-store-id="')[1].split('"')[0]
            if phone == "" and '<p itemprop="telephone">' in line2:
                phone = line2.split('<p itemprop="telephone">')[1].split("<")[0]
        hours = hours.replace(" : ", ": ")
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if "%" in city:
            city = city.split("%")[0]
        city = city.strip()
        if "Manchester" in city:
            city = "Manchester"
        if "Staples" in name:
            city = "London"
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
