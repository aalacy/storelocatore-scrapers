import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("amtrak_com")

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
    locs = []
    canada = [
        "SK",
        "ON",
        "PQ",
        "QC",
        "AB",
        "MB",
        "BC",
        "YT",
        "NS",
        "NF",
        "NL",
        "PEI",
        "PE",
    ]
    url = "https://www.amtrak.com/sitemap.xml"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if "<loc>https://www.amtrak.com/stations/" in line:
            items = line.split("<loc>https://www.amtrak.com/stations/")
            for item in items:
                if "<?xml" not in item:
                    lurl = (
                        "https://maps.amtrak.com/services/MapDataService/StationInfo/getStationInfo?stationCode="
                        + item.split("<")[0]
                    )
                    locs.append(lurl)
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        website = "amtrak.com"
        typ = "<MISSING>"
        hours = ""
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        country = "US"
        lat = "<MISSING>"
        lng = "<MISSING>"
        phone = "215-856-7924"
        store = loc.rsplit("=", 1)[1]
        lurl = "https://www.amtrak.com/content/amtrak/en-us/stations/" + store + ".html"
        r2 = session.get(lurl, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if '<h1 class="hero-banner-and-info__card_info-title">' in line2:
                name = line2.split(
                    '<h1 class="hero-banner-and-info__card_info-title">'
                )[1].split("<")[0]
            if add == "" and 'ard_block-address">' in line2:
                add = line2.split('ard_block-address">')[1].split("<")[0]
            if add != "" and 'ard_block-address">' in line2 and "-->" not in line2:
                if add not in line2 and ", " in line2:
                    csz = line2.split('card_block-address">')[1].split("<")[0].strip()
                    city = csz.split(",")[0]
                    state = csz.split(",")[1].strip().split(" ")[0]
                    zc = csz.rsplit(" ", 1)[1]
            if 'station-type">' in line2:
                typ = line2.split('station-type">')[1].split("<")[0]
            if "maps/dir//" in line2:
                lat = line2.split("maps/dir//")[1].split(",")[0]
                lng = line2.split("maps/dir//")[1].split(",")[1].split('"')[0]
        hurl = (
            "https://www.amtrak.com/content/amtrak/en-us/stations/"
            + store.lower()
            + ".stationTabContainer."
            + store.upper()
            + ".json"
        )
        r3 = session.get(hurl, headers=headers)
        if r3.encoding is None:
            r3.encoding = "utf-8"
        for line3 in r3.iter_lines(decode_unicode=True):
            if '"type":"stationhours","rangeData":[{' in line3:
                days = (
                    line3.split('"type":"stationhours","rangeData":[{')[1]
                    .split("}]}]},")[0]
                    .split('"day":"')
                )
                for day in days:
                    if "timeSlot" in day:
                        hrs = (
                            day.split('"')[0]
                            + ": "
                            + day.split('"timeSlot":"')[1].split('"')[0]
                        )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        if state in canada:
            country = "CA"
        if "(" in typ:
            typ = typ.split("(")[0].strip()
        if add != "":
            yield [
                website,
                lurl,
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
