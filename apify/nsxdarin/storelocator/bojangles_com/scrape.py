import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bojangles_com")

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
    url = "https://locations.bojangles.com/sitemap.xml"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if "<loc>https://locations.bojangles.com/" in line:
            lurl = line.split(">")[1].split("<")[0]
            count = lurl.count("/")
            if count == 5:
                locs.append(lurl)
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        website = "bojangles.com"
        typ = "Restaurant"
        hours = ""
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines(decode_unicode=True):
            if "Bojangles </span>" in line2:
                name = line2.split("Bojangles </span>")[1].split("<")[0].strip()
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
            if '<span class="c-address-street-1 ">' in line2:
                add = line2.split('<span class="c-address-street-1 ">')[1].split("<")[0]
                try:
                    add = (
                        add
                        + " "
                        + line2.split('<span class="c-address-street-2 ">')[1].split(
                            "<"
                        )[0]
                    )
                except:
                    pass
                add = add.strip()
                city = line2.split('<span itemprop="addressLocality">')[1].split("<")[0]
                state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0].strip()
                country = "US"
                try:
                    phone = line2.split('c-phone-main-number-link" href="tel:')[
                        1
                    ].split('"')[0]
                except:
                    phone = "<MISSING>"
            if '{"ids":' in line2:
                store = line2.split('{"ids":')[1].split(",")[0]
            if 'c-location-hours-details-row-day">' in line2:
                days = line2.split('c-location-hours-details-row-day">')
                for day in days:
                    if (
                        '</td><td class="c-location-hours-details-row-intervals">'
                        in day
                        and "Open 24 hours" not in day
                        and "Closed" in day
                    ):
                        hrs = day.split("<")[0] + ": Closed"
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
                    if (
                        '</td><td class="c-location-hours-details-row-intervals">'
                        in day
                        and "Open 24 hours" not in day
                        and "Closed" not in day
                    ):
                        hrs = (
                            day.split("<")[0]
                            + ": "
                            + day.split('row-intervals-instance-open">')[1].split("<")[
                                0
                            ]
                            + "-"
                            + day.split('intervals-instance-close">')[1].split("<")[0]
                        )
                        hrs = hrs.replace(" am", "am")
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
                    if (
                        '</td><td class="c-location-hours-details-row-intervals">'
                        in day
                        and "Open 24 Hours" in day
                    ):
                        hours = day.split("<")[0] + ": Open 24 Hours"
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        if "blytheville/3910" in loc or "marion/1900" in loc:
            hours = "Mon-Sun: Open 24 hours"
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
