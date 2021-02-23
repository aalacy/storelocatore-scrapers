import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("stjosephhealth_org")


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
    website = "stjosephhealth.org"
    country = "US"
    typ = "<MISSING>"
    store = "<MISSING>"
    for x in range(1, 151):
        logger.info("Page " + str(x))
        url = (
            "https://www.providence.org/locations?postal=90009&lookup=&lookupvalue=&page="
            + str(x)
            + "&radius=5000&term="
        )
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '<div class="subhead-h3"><a href="' in line:
                lurl = (
                    "https://www.providence.org"
                    + line.split('<div class="subhead-h3"><a href="')[1].split('"')[0]
                )
                if lurl not in locs:
                    locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"name":"' in line2:
                name = line2.split('"name":"')[1].split('"')[0]
                try:
                    hours = line2.split(',"openingHours":"')[1].split('"')[0]
                except:
                    hours = "<MISSING>"
                try:
                    add = line2.split('"streetAddress":"')[1].split('"')[0]
                except:
                    add = "<MISSING>"
                try:
                    state = line2.split('"addressRegion":"')[1].split('"')[0]
                except:
                    state = "<MISSING>"
                try:
                    zc = line2.split('"postalCode":"')[1].split('"')[0]
                except:
                    zc = "<MISSING>"
                try:
                    city = line2.split('"addressLocality":"')[1].split('"')[0]
                except:
                    city = "<MISSING>"
                try:
                    phone = line2.split('"telephone":"')[1].split('"')[0]
                except:
                    phone = "<MISSING>"
                try:
                    lat = line2.split('"latitude":')[1].split(",")[0]
                except:
                    lat = "<MISSING>"
                try:
                    lng = line2.split('"longitude":')[1].split("}")[0]
                except:
                    lng = "<MISSING>"
                try:
                    typ = line2.split('"@type":"')[1].split('"')[0]
                except:
                    typ = "<MISSING>"
        if typ != "<MISSING>" and name != "":
            if add == "":
                add = "<MISSING>"
            if city == "":
                city = "<MISSING>"
            if zc == "":
                zc = "<MISSING>"
            if phone == "":
                phone = "<MISSING>"
            if hours == "":
                hours = "<MISSING>"
            if state == "":
                state = "<MISSING>"
            name = name.replace("\\u0027", "'")
            add = add.replace("\\u0027", "'")
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
