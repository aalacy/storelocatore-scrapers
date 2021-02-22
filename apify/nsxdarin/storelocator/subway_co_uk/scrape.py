import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("subway_co_uk")


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
    states = [
        "https://restaurants.subway.com/united-kingdom/en",
        "https://restaurants.subway.com/united-kingdom/ni",
        "https://restaurants.subway.com/united-kingdom/wa",
        "https://restaurants.subway.com/united-kingdom/sc",
    ]
    cities = []
    website = "subway.co.uk"
    typ = "<MISSING>"
    country = "GB"
    for state in states:
        logger.info(state)
        r = session.get(state, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '"Directory-listLink" href="../' in line:
                items = line.split('"Directory-listLink" href="../')
                for item in items:
                    if 'data-count="(' in item:
                        count = item.split('data-count="(')[1].split(")")[0]
                        lurl = "https://restaurants.subway.com/" + item.split('"')[0]
                        if count == "1":
                            locs.append(lurl + "|" + state.split("kingdom/")[1])
                        else:
                            cities.append(lurl + "|" + state.split("kingdom/")[1])
    for city in cities:
        logger.info(city.split("|")[0])
        r2 = session.get(city.split("|")[0], headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<div class="Teaser-innerWrapper"><a href="../../' in line2:
                items = line2.split('<div class="Teaser-innerWrapper"><a href="../../')
                for item in items:
                    if 'class="Teaser-title" data-ya-track="visitpage">' in item:
                        locs.append(
                            "https://restaurants.subway.com/"
                            + item.split('"')[0]
                            + "|"
                            + city.split("|")[1]
                        )
    for loc in locs:
        purl = loc.split("|")[0]
        state = loc.split("|")[1].upper()
        logger.info(purl)
        name = ""
        add = ""
        city = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(purl, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'itemprop="name">' in line2:
                name = (
                    line2.split('itemprop="name">')[1]
                    .split("</h1>")[0]
                    .replace("<br>", "")
                    .replace("  ", " ")
                    .replace("  ", " ")
                )
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[
                    0
                ]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[
                    0
                ]
            if add == "" and '<span class="c-address-street-1">' in line2:
                add = line2.split('<span class="c-address-street-1">')[1].split("<")[0]
                city = line2.split('<span class="c-address-city">')[1].split("<")[0]
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
            if phone == "" and "Main Number</div>" in line2:
                phone = (
                    line2.split("Main Number</div>")[1]
                    .split('"Phone-link" href="tel:')[1]
                    .split('"')[0]
                )
            if hours == "" and "<th>Hours</th>" in line2:
                days = (
                    line2.split("Hours</th>")[1]
                    .split("</div></div></div>")[0]
                    .split('"c-hours-details-row-day">')
                )
                for day in days:
                    if 'c-hours-details-row-intervals">' in day:
                        if "Closed</td>" in day:
                            hrs = day.split("<")[0] + ": Closed"
                        elif "Open 24 hours" in day:
                            hrs = day.split("<")[0] + ": Open 24 Hours"
                        else:
                            hrs = (
                                day.split("<")[0]
                                + ": "
                                + day.split('-instance-open">')[1].split("<")[0]
                                + "-"
                                + day.split('-instance-close">')[1].split("<")[0]
                            )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        yield [
            website,
            purl,
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
