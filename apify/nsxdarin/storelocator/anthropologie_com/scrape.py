import csv
from sgrequests import SgRequests
import time

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
    url = "https://www.anthropologie.com/stores#?viewAll=true"
    session = SgRequests()
    r = session.get(url, headers=headers)
    Found = True
    for line in r.iter_lines(decode_unicode=True):
        if "Paris" in line:
            Found = False
        if "England" in line:
            Found = True
        if (
            'itemprop="url" content="https://www.anthropologie.com/stores">' in line
            and Found
        ):
            lurl = (
                "https://www.anthropologie.com" + line.split('href="')[1].split('"')[0]
            )
            if lurl != "https://www.anthropologie.com/stores":
                locs.append(lurl)
    for loc in locs:
        time.sleep(3)
        session = SgRequests()
        website = "anthropologie.com"
        typ = "<MISSING>"
        hours = ""
        name = ""
        add = ""
        city = ""
        state = ""
        country = "US"
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines(decode_unicode=True)
        Found = False
        for line2 in lines:
            if "<h2>Hours</h2>" in line2:
                Found = True
            if Found and "</ul>" in line2:
                Found = False
            if Found and "day:" in line2:
                hrs = (
                    line2.strip().replace("\r", "").replace("\n", "").replace("\t", "")
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if '<span itemprop="streetAddress">' in line2:
                add = line2.split('<span itemprop="streetAddress">')[1].split("<")[0]
            if '<span itemprop="addressLocality">' in line2:
                city = line2.split('<span itemprop="addressLocality">')[1].split("<")[0]
            if '<span itemprop="addressRegion">' in line2:
                state = line2.split('<span itemprop="addressRegion">')[1].split("<")[0]
            if '<span itemprop="postalCode">' in line2:
                zc = line2.split('<span itemprop="postalCode">')[1].split("<")[0]
            if '<span itemprop="telephone">' in line2:
                phone = line2.split('<span itemprop="telephone">')[1].split("<")[0]
            if 'property="og:title" content="' in line2:
                name = line2.split('property="og:title" content="')[1].split('"')[0]
            if '<meta property="place:location:latitude"  content="' in line2:
                lng = line2.split(
                    '<meta property="place:location:latitude"  content="'
                )[1].split('"')[0]
            if '<meta property="place:location:longitude" content="' in line2:
                lat = line2.split(
                    '<meta property="place:location:longitude" content="'
                )[1].split('"')[0]
        if state == "England" or state == "Wales" or state == "Scotland":
            country = "GB"
        canada = [
            "MB",
            "AB",
            "QC",
            "PE",
            "PEI",
            "NL",
            "NS",
            "NT",
            "NU",
            "YK",
            "BC",
            "ON",
        ]
        if state in canada:
            country = "CA"
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        hours = hours.replace("CLOSED - CLOSED", "CLOSED")
        Closed = False
        if "Closed" in name and "Temp" not in name:
            Closed = True
        if Closed is False:
            if "Leeds" in name or "Belfast" in name:
                country = "GB"
            if "FN-ES" not in state and "FN-DE" not in state:
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
