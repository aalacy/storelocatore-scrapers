import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("fastenal_com")

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
    url = "https://www.fastenal.com/locations/all"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    styp = ""
    for line in r.iter_lines(decode_unicode=True):
        if "Distribution Centers" in line:
            styp = "Distribution Center"
        if "Branch Locations" in line:
            styp = "Branch"
        if styp != "" and '<td><a href="/locations/details/' in line:
            lurl = "https://www.fastenal.com" + line.split('href="')[1].split('"')[0]
            lurl = lurl.split(";jsession")[0]
            locs.append(lurl + "|" + styp)
    for loc in locs:
        r2 = session.get(loc.split("|")[0], headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        logger.info(("Pulling Location %s..." % loc.split("|")[0]))
        website = "fastenal.com"
        typ = loc.split("|")[1]
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        country = ""
        phone = ""
        lat = ""
        lng = ""
        HFound = False
        store = loc.split("|")[0].rsplit("/", 1)[1]
        hours = ""
        for line2 in r2.iter_lines(decode_unicode=True):
            if "<h1>" in line2 and name == "":
                name = line2.split("<h1>")[1].split("<")[0]
            if 'class="address1 ellipsis">' in line2:
                add = line2.split('class="address1 ellipsis">')[1].split("<")[0]
            if '<span class="city">' in line2:
                city = line2.split('<span class="city">')[1].split("<")[0]
            if '<span class="stateAbbreviation">' in line2:
                state = line2.split('<span class="stateAbbreviation">')[1].split("<")[0]
            if '<span class="countryAbbreviation">' in line2:
                country = line2.split('<span class="countryAbbreviation">')[1].split(
                    "<"
                )[0]
                if country == "USA":
                    country = "US"
                if country == "CAN":
                    country = "CA"
                if country == "GBR":
                    country = "GB"
            if 'class="postalCode">' in line2:
                zc = line2.split('class="postalCode">')[1].split("<")[0]
            if 'P:<a href="tel:' in line2:
                phone = line2.split('P:<a href="tel:')[1].split('"')[0].strip()
            if "googleMaps.lat = " in line2:
                lat = line2.split("googleMaps.lat = ")[1].split(";")[0].strip()
            if "googleMaps.longitude = " in line2:
                lng = line2.split("googleMaps.longitude = ")[1].split(";")[0].strip()
            if "Hours" in line2:
                HFound = True
            if HFound and "<div" in line2:
                HFound = False
            if HFound and "<p>" in line2:
                hrs = (
                    line2.strip().replace("\t", "").replace("\n", "").replace("\r", "")
                )
                hrs = hrs.replace("<p>", "").replace("</p>", "")
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if country == "CA" or country == "US" or country == "GB":
            if phone == "":
                phone = "<MISSING>"
            if hours == "":
                hours = "<MISSING>"
            name = name.replace("&#039;", "'").replace("&amp;", "&")
            if state == "":
                state = "<MISSING>"
            if zc == "":
                zc = "<MISSING>"
            city = city.replace("&#039;", "'").replace("&amp;", "&")
            hours = hours.replace("&#039;", "'").replace("&amp;", "&")
            add = add.replace("&#039;", "'").replace("&amp;", "&")
            if "MN100" not in name:
                yield [
                    website,
                    loc.split("|")[0],
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
