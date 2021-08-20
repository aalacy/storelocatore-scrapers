import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("advancedbldg_com")


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
    url = "https://advancedbldg.com"
    r = session.get(url, headers=headers)
    website = "advancedbldg.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "content: '<a href=\"Branch.aspx?BranchId=" in line:
            locs.append(
                "https://advancedbldg.com/Branch.aspx?BranchId="
                + line.split("Branch.aspx?BranchId=")[1].split('"')[0]
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
            if '<span id="ContentPlaceHolder1_BranchName">' in line2:
                name = line2.split('<span id="ContentPlaceHolder1_BranchName">')[
                    1
                ].split("<")[0]
            if 'ContentPlaceHolder1_StreetAddr">' in line2:
                add = line2.split('ContentPlaceHolder1_StreetAddr">')[1].split("<")[0]
            if 'ContentPlaceHolder1_City">' in line2:
                city = line2.split('ContentPlaceHolder1_City">')[1].split("<")[0]
            if 'ContentPlaceHolder1_StateCd">' in line2:
                state = line2.split('ContentPlaceHolder1_StateCd">')[1].split("<")[0]
            if 'ZipCd">' in line2:
                zc = line2.split('ZipCd">')[1].split("<")[0]
            if 'Phone:</strong> <a href="tel:' in line2:
                phone = line2.split('Phone:</strong> <a href="tel:')[1].split('"')[0]
            if 'BusinessHours">' in line2:
                hours = line2.split('BusinessHours">')[1].split("<")[0]
            if "LatLng(" in line2:
                lat = line2.split("LatLng(")[1].split(",")[0]
                lng = line2.split("LatLng(")[1].split(",")[1].strip().split(")")[0]
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
