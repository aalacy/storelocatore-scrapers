import csv
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("goldencorral_com")

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
    for x in range(-60, -170, -3):
        for y in range(15, 65, 3):
            lat1 = y
            lat2 = y + 3
            lat3 = y - 3
            lng1 = x
            lng2 = x + 3
            lng3 = x - 3
            logger.info((str(lat1) + "," + str(lng1)))
            url = (
                "https://www.goldencorral.com/locations/wp-json/locator/v1/search/"
                + str(lat1)
                + "/"
                + str(lng1)
                + "/"
                + str(lat3)
                + "/"
                + str(lng3)
                + "/"
                + str(lat2)
                + "/"
                + str(lng2)
            )
            r = session.get(url, headers=headers)
            if r.encoding is None:
                r.encoding = "utf-8"
            for item in json.loads(r.content):
                lat = item["lat"]
                lng = item["lng"]
                name = item["company"]
                store = item["customer"]
                add = item["address"]
                city = item["city"]
                state = item["state"]
                zc = item["zip"]
                phone = item["phone"]
                country = "US"
                hours = ""
                opening_soon = item["opening_soon"]
                if opening_soon == "0" and store not in locs:
                    locs.append(store)
                    website = "goldencorral.com"
                    typ = "<MISSING>"
                    addtext = (
                        add.split(" ", 1)[1].replace(".", "").lower().replace(" ", "-")
                    )
                    loc = (
                        "https://www.goldencorral.com/locations/location-detail/"
                        + store
                        + "/golden-corral-"
                        + addtext
                    )
                    loc = loc.replace("#", "").replace(",", "")
                    try:
                        r = session.get(loc, headers=headers)
                        if r.encoding is None:
                            r.encoding = "utf-8"
                        lines = r.iter_lines(decode_unicode=True)
                        for line in lines:
                            if '<ul class="location-detail-hours">' in line:
                                items = line.split("<li><span>")
                                for item in items:
                                    if "<time" in item:
                                        hrs = item.split("<")[0] + ": "
                                        if 'class="subheading-s"></time>' in item:
                                            hrs = hrs + "Closed"
                                        else:
                                            hrs = (
                                                hrs
                                                + item.split('class="subheading-s">')[
                                                    1
                                                ].split("<")[0]
                                            )
                                        if hours == "":
                                            hours = hrs
                                        else:
                                            hours = hours + "; " + hrs
                    except:
                        pass
                    if hours == "":
                        hours = "<MISSING>"
                    if phone == "":
                        phone = "<MISSING>"
                    if hours == "<MISSING>":
                        hours = "INACCESSIBLE"
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
    website = "goldencorral.com"
    typ = "<MISSING>"
    country = "US"
    name = "Golden Corral 2709"
    add = "1734 W. 49th Street"
    city = "Hialeah"
    loc = "https://www.goldencorral.com/locations/location-detail/2709/golden-corral-w-49th-street/"
    state = "FL"
    zc = "33012"
    phone = "786-245-8997"
    store = "2709"
    hours = (
        "Mon-Thu: 11:00AM - 10:00PM; Fri-Sat: 8:00AM - 11:00PM; Sun: 8:00AM - 10:00PM"
    )
    lat = "25.8665337"
    lng = "-80.3170877"
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
