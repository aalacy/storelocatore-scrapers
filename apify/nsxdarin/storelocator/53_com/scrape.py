import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("53_com")

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
    url = "https://locations.53.com/sitemap.xml"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if "<loc>https://locations.53.com/" in line:
            lurl = line.split(">")[1].split("<")[0]
            count = lurl.count("/")
            if count >= 5:
                locs.append(lurl)
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        website = "53.com"
        typ = "Branch"
        name = ""
        add = ""
        city = ""
        state = ""
        phone = ""
        zc = ""
        lat = ""
        lng = ""
        country = "US"
        hours = ""
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<span class="name">' in line2:
                name = (
                    line2.split('<span class="name">')[1]
                    .split("</span></span>")[0]
                    .replace('</span> <span class="geomodifier">', " ")
                )
                if "<" in name:
                    name = name.split("<")[0]
                typ = line2.split('<div class="location-type">')[1].split("<")[0]
                add = line2.split("c-address-street-1")[1].split('">')[1].split("<")[0]
                city = (
                    line2.split('class="c-address-city')[1].split('">')[1].split("<")[0]
                )
                state = line2.split('"c-address-state')[1].split(">")[1].split("<")[0]
                zc = (
                    line2.split(' class="c-address-postal-code')[1]
                    .split(">")[1]
                    .split("<")[0]
                    .strip()
                )
                phone = line2.split('href="tel:')[1].split('">')[1].split("<")[0]
                days = (
                    line2.split("data-days='")[1].split("}]' data")[0].split('"day":"')
                )
                if '"intervals"' not in line2.split("data-days='")[1].split("}]' data")[
                    0
                ].split('"day":"'):
                    days = (
                        line2.split("data-days='")[2]
                        .split("}]' data")[0]
                        .split('"day":"')
                    )
                for day in days:
                    if '"intervals"' in day:
                        if '"intervals":[]' in day:
                            hrs = day.split('"')[0] + ": Closed"
                        else:
                            hrs = (
                                day.split('"')[0]
                                + ": "
                                + day.split('"start":')[1].split("}")[0]
                                + "-"
                                + day.split('"end":')[1].split(",")[0]
                            )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        lat = "<MISSING>"
        lng = "<MISSING>"
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        store = "<MISSING>"
        add = add.replace("[{: Closed;", "").strip()
        if "effingham/200-east-jefferson-ave" in loc:
            add = "200 East Jefferson Ave"
            city = "Effingham"
            state = "IL"
            zc = "62401"
            phone = "(217) 342-5700"
            name = "Fifth Third Bank Effingham"
            hours = "MONDAY: 900-1700; TUESDAY: 900-1700; WEDNESDAY: 900-1700; THURSDAY: 900-1700; FRIDAY: 900-1800; SATURDAY: 900-1200; SUNDAY: Closed"
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
