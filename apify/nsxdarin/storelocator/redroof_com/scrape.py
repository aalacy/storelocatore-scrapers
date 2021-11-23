import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("redroof_com")


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
    alllocs = []
    url = "https://www.redroof.com/hotel-sitemap"
    session = SgRequests()
    r = session.get(url, headers=headers)
    website = "redroof.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            '<p xmlns="http://www.w3.org/1999/xhtml"><a href="https://www.redroof.com/property/'
            in line
        ):
            items = line.split(
                '<p xmlns="http://www.w3.org/1999/xhtml"><a href="https://www.redroof.com/property/'
            )
            for item in items:
                if '<div id="react-newhome"><div class="header-wrapper ">' not in item:
                    locs.append(
                        "https://www.redroof.com/property/" + item.split('"')[0]
                    )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = "<MISSING>"
        session = SgRequests()
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<span class="name" itemProp="name">' in line2:
                name = (
                    line2.split('<span class="name" itemProp="name">')[1]
                    .split("<")[0]
                    .strip()
                )
            if 'Street1\\":\\"' in line2:
                add = line2.split('Street1\\":\\"')[1].split("\\")[0]
                zc = line2.split('"PostalCode\\":\\"')[1].split("\\")[0]
                state = line2.split('"State\\":\\"')[1].split("\\")[0]
                city = line2.split('"City\\":\\"')[1].split("\\")[0]
                lat = line2.split('"Latitude\\":\\"')[1].split("\\")[0]
                lng = line2.split('"Longitude\\":\\"')[1].split("\\")[0]
                phone = line2.split('"PhoneNumber\\":\\"')[1].split("\\")[0]
        if state == "AB":
            country = "CA"
        else:
            country = "US"
        intl = ["OT", "FU", "RJ", "SP"]
        if "1051 Tiffany" in add:
            state = "OH"
        if "," in city:
            city = city.split(",")[0].strip()
        city = city.replace(" area", "")
        if state not in intl and "troy/11191" not in loc:
            if city == "":
                city = "<MISSING>"
            if zc == "":
                zc = "<MISSING>"
            if state == "":
                state = "<MISSING>"
            if phone == "":
                phone = "<MISSING>"
            if lat == "":
                lat = "<MISSING>"
            if lng == "":
                lng = "<MISSING>"
            if name == "":
                name = "<MISSING>"
            if add == "":
                add = "<MISSING>"
            if "RRI867" in loc:
                city = "Biloxi"
            if state != "<MISSING>":
                if loc not in alllocs:
                    alllocs.append(loc)
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
