import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import time

logger = SgLogSetup().get_logger("fastenal_com__dc")

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
    session = SgRequests()
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
        time.sleep(3)
        session = SgRequests()
        r2 = session.get(loc.split("|")[0], headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        logger.info(("Pulling Location %s..." % loc.split("|")[0]))
        website = "fastenal.com/dc"
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
            if HFound and "</p>" in line2 and "<p>" not in line2:
                hrs = (
                    hrs
                    + " "
                    + line2.split("</p>")[0]
                    .strip()
                    .replace("  ", " ")
                    .replace("\t", "")
                )
        if country == "CA" or country == "US":
            if phone == "":
                phone = "<MISSING>"
            if hours == "":
                hours = "<MISSING>"
            name = name.replace("&#039;", "'").replace("&amp;", "&")
            city = city.replace("&#039;", "'").replace("&amp;", "&")
            hours = hours.replace("&#039;", "'").replace("&amp;", "&")
            add = add.replace("&#039;", "'").replace("&amp;", "&")
            if "; For" in hours:
                hours = hours.split("; For")[0]
            hours = hours.replace("Open to the public", "").strip()
            if "; Off" in hours:
                hours = hours.split("; Off")[0]
            if "; Doug" in hours:
                hours = hours.split("; Doug")[0]
            if "; Hours" in hours:
                hours = hours.split("; Hours")[0]
            if "; Bath" in hours:
                hours = hours.split("; Bath")[0]
            if "; South" in hours:
                hours = hours.split("; South")[0]
            if "; Please" in hours:
                hours = hours.split("; Please")[0]
            if "; Place" in hours:
                hours = hours.split("; Place")[0]
            if "; Order" in hours:
                hours = hours.split("; Order")[0]
            if "; Beside" in hours:
                hours = hours.split("; Beside")[0]
            if "; High" in hours:
                hours = hours.split("; High")[0]
            if "; From" in hours:
                hours = hours.split("; From")[0]
            if "; emer" in hours:
                hours = hours.split("; emer")[0]
            if " / " in hours:
                hours = hours.split(" / ")[0]
            if "; Head" in hours:
                hours = hours.split("; Head")[0]
            if "; 864" in hours:
                hours = hours.split("; 864")[0]
            if "; Open" in hours:
                hours = hours.split("; Open")[0]
            if "; West" in hours:
                hours = hours.split("; West")[0]
            if "; Turn" in hours:
                hours = hours.split("; Turn")[0]
            if "; City" in hours:
                hours = hours.split("; City")[0]
            if "; Take" in hours:
                hours = hours.split("; Take")[0]
            if "; Aldine" in hours:
                hours = hours.split("; Aldine")[0]
            if "; Store" in hours:
                hours = hours.split("; Store")[0]
            if "; On " in hours:
                hours = hours.split("; On ")[0]
            if "; East" in hours:
                hours = hours.split("; East")[0]
            if "; 1 m" in hours:
                hours = hours.split("; 1 m")[0]
            if "; just" in hours:
                hours = hours.split("; just")[0]
            if "; Just" in hours:
                hours = hours.split("; Just")[0]
            if "; Route" in hours:
                hours = hours.split("; Route")[0]
            if "; 1/4" in hours:
                hours = hours.split("; 1/4")[0]
            if "; 122" in hours:
                hours = hours.split("; 122")[0]
            if "; Locate" in hours:
                hours = hours.split("; Locate")[0]
            if "; DO NOT" in hours:
                hours = hours.split("; DO NOT")[0]
            if "; Customer" in hours:
                hours = hours.split("; Customer")[0]
            if "; Cross" in hours:
                hours = hours.split("; Cross")[0]
            if "; FROM" in hours:
                hours = hours.split("; FROM")[0]
            if "; GM" in hours:
                hours = hours.split("; GM")[0]
            if "; South" in hours:
                hours = hours.split("; South")[0]
            if "; Univ" in hours:
                hours = hours.split("; Univ")[0]
            if "; Trav" in hours:
                hours = hours.split("; Trav")[0]
            if "Due to Covid" in hours:
                hours = hours.split("Due to")[0].strip()
            if "/ W" in hours:
                hours = hours.split("/ W")[0].strip()
            if ";" not in hours and ":" not in hours and "0" not in hours:
                hours = "<MISSING>"
            if " (" in hours:
                hours = hours.split(" (")[0]
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
