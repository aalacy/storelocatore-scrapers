import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("southernshingles_com")


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
    url = "https://southernshingles.com"
    r = session.get(url, headers=headers)
    website = "southernshingles.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a href="Branch.aspx?' in line:
            locs.append(
                "https://southernshingles.com/Branch.aspx?BranchId="
                + line.split("BranchId=")[1].split('"')[0]
            )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.split("BranchId=")[1].split("&")[0]
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "new google.maps.LatLng(" in line2:
                lat = line2.split("new google.maps.LatLng(")[1].split(",")[0]
                lng = line2.split(",")[1].split(")")[0].strip()
            if '<span id="ContentPlaceHolder1_BranchShortName">' in line2:
                name = line2.split('<span id="ContentPlaceHolder1_BranchShortName">')[
                    1
                ].split("<")[0]
            if 'StreetAddr">' in line2:
                add = line2.split('StreetAddr">')[1].split("<")[0]
            if 'Holder1_City">' in line2:
                city = line2.split('Holder1_City">')[1].split("<")[0]
                state = line2.split('StateCd">')[1].split("<")[0]
                zc = line2.split('ZipCd">')[1].split("<")[0]
            if phone == "" and '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if 'BusinessHours">' in line2:
                hours = line2.split('BusinessHours">')[1].split("<")[0]
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
