import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("lkqpickyourpart_com")


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
    url = "https://www.lkqpickyourpart.com/locations/"
    r = session.get(url, headers=headers)
    website = "lkqpickyourpart.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"pypfys_links"><a href="/' in line:
            items = line.split('"pypfys_links"><a href="/')
            for item in items:
                if "Store Info<" in item:
                    locs.append(
                        "https://www.lkqpickyourpart.com"
                        + item.split('href="')[1]
                        .split('"')[0]
                        .replace("part-interchange-search/", "")
                    )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"name" : "' in line2:
                name = line2.split('"name" : "')[1].split('"')[0]
            if '"streetAddress" : "' in line2:
                add = line2.split('"streetAddress" : "')[1].split('"')[0]
            if '"addressLocality" : "' in line2:
                city = line2.split('"addressLocality" : "')[1].split('"')[0]
            if '"addressRegion" : "' in line2:
                state = line2.split('"addressRegion" : "')[1].split('"')[0]
            if '"addressCountry" : "' in line2:
                country = line2.split('"addressCountry" : "')[1].split('"')[0]
            if '"postalCode" : "' in line2:
                zc = line2.split('"postalCode" : "')[1].split('"')[0]
            if '"latitude": ' in line2:
                lat = line2.split('"latitude": ')[1].split(",")[0]
            if '"longitude": ' in line2:
                lng = (
                    line2.split('"longitude": ')[1]
                    .strip()
                    .replace("\t", "")
                    .replace("\r", "")
                    .replace("\n", "")
                )
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0].replace("+1", "")
            if 'id="pyploc_info" data-store="' in line2:
                store = line2.split('id="pyploc_info" data-store="')[1].split('"')[0]
            if '"pyploc_hours">' in line2:
                hours = (
                    line2.split('"pyploc_hours">')[1]
                    .split("</div>")[0]
                    .replace("</p><p>", "; ")
                    .replace("<p>", "")
                    .replace("</p>", "")
                    .replace(
                        '<p id="pyploc_admissionsNote">Must Be 16 Years Old To Enter Facility',
                        "",
                    )
                    .strip()
                )
                if "<" in hours:
                    hours = hours.split("<")[0].strip()
        if "Quebec" in state:
            country = "CA"
        if "(Parts)" in add:
            add = add.split("(Parts)")[0].strip()
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
