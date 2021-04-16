import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("apple_com__retail")


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
    url = "https://www.apple.com/retail/storelist/"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if 'hrefLang="en-US" href="/retail/' in line:
            items = line.split('hrefLang="en-US" href="/retail/')
            for item in items:
                if "</a></span></div></div>" in item:
                    locs.append("https://www.apple.com/" + item.split('"')[0])
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        website = "apple.com/retail"
        typ = "<MISSING>"
        hours = ""
        name = ""
        city = ""
        add = ""
        zc = ""
        country = "US"
        state = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if '<div class="store-detail-heading-name"><h1>' in line2:
                name = line2.split('<div class="store-detail-heading-name"><h1>')[
                    1
                ].split("<")[0]
            if '"streetAddress":"' in line2:
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                state = line2.split('"addressRegion":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                phone = line2.split('"telephone":"')[1].split('"')[0]
                lat = line2.split('{"@type":"GeoCoordinates","latitude":')[1].split(
                    ","
                )[0]
                lng = (
                    line2.split('{"@type":"GeoCoordinates"')[1]
                    .split('longitude":')[1]
                    .split("}")[0]
                )
            if '<td class="store-open-hours-day">' in line2:
                days = line2.split('<td class="store-open-hours-day">')
                for day in days:
                    if '"store-open-hours-span' in day:
                        hrs = (
                            day.split("<")[0]
                            + ": "
                            + day.split('"store-open-hours-span')[1]
                            .split('">')[1]
                            .split("<")[0]
                            .strip()
                        )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        daylist = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        for dname in daylist:
            if dname not in hours:
                hours = hours.replace("Today", dname)
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
