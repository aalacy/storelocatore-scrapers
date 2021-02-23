import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("primark_com")


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
    infos = []
    for x in range(0, 7):
        url = "https://stores.primark.com/sitemap.xml." + str(x)
        r = session.get(url, headers=headers)
        logger.info("Pulling Stores")
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if (
                'hreflang="en_US" href="https://stores.primark.com/en_us/canada/'
                in line
            ):
                locs.append(line.split('href="')[1].split('"')[0])
            if (
                'hreflang="en_US" href="https://stores.primark.com/en_us/united-states/'
                in line
            ):
                locs.append(line.split('href="')[1].split('"')[0])
            if (
                'hreflang="en_US" href="https://stores.primark.com/en_us/united-kingdom/'
                in line
            ):
                locs.append(line.split('href="')[1].split('"')[0])
    for loc in locs:
        typ = "<MISSING>"
        website = "primark.com"
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        country = "US"
        Closed = False
        if "-kingdom/" in loc or "-states/" in loc:
            if "-kingdom/" in loc:
                country = "GB"
            else:
                country = "US"
            r2 = session.get(loc, headers=headers)
            for line2 in r2.iter_lines():
                line2 = str(line2.decode("utf-8"))
                if 'c-hours-details-row-intervals">Temporarily Closed' in line2:
                    Closed = True
                if "<title>" in line2:
                    name = line2.split("<title>")[1].split("|")[0].strip()
                if '"line1":"' in line2:
                    add = line2.split('"line1":"')[1].split('"')[0]
                    try:
                        add = add + " " + line2.split('"line2":"')[1].split('"')[0]
                    except:
                        pass
                    try:
                        add = add + " " + line2.split('"line3":"')[1].split('"')[0]
                    except:
                        pass
                    add = add.strip()
                    zc = line2.split('"postalCode":"')[1].split('"')[0]
                    city = line2.split('"city":"')[1].split('"')[0]
                    try:
                        state = line2.split('"region":"')[1].split('"')[0]
                    except:
                        state = "<MISSING>"
                    phone = (
                        line2.split('"mainPhone":')[1]
                        .split('"display":"')[1]
                        .split('"')[0]
                    )
                if 'itemprop="latitude" content="' in line2:
                    lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
                    lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
                if '"openingHours" content="' in line2:
                    days = line2.split('"openingHours" content="')
                    for day in days:
                        if '<td class="c-hours-details-row-day"' in day:
                            hrs = day.split('"')[0]
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
            if add != "":
                if "1 Chequers Mall" in add:
                    hours = "Mon-Sat: 8:00-20:00; Sun: 11:00-17:00"
                addinfo = add + "|" + city + "|" + zc
                if addinfo not in infos:
                    infos.append(addinfo)
                    if Closed:
                        hours = "Temporary Closed"
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
