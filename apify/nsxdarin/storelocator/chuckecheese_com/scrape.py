import csv
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("chuckecheese_com")

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "Content-Type": "application/json; charset=UTF-8",
    "Authorization": "Basic TG9jYXRpb246OUQ2QjFCREEtRDVDNC00Q0VDLTgxQTktOEUzRTU2OUVCNENC",
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
    coord = [
        "13.4,144.7",
        "18,-66",
        "60,-150",
        "20,-155",
        "45,-120",
        "45,-115",
        "35,-120",
        "35,-115",
        "45,-110",
        "35,-110",
        "45,-105",
        "35,-105",
        "45,-100",
        "35,-100",
        "45,-95",
        "35,-95",
        "45,-90",
        "35,-90",
        "45,-85",
        "35,-85",
        "45,-80",
        "35,-80",
        "45,-75",
        "35,-75",
        "45,-70",
        "35,-70",
    ]
    coord.append("50,-120")
    coord.append("50,-115")
    coord.append("50,-110")
    coord.append("50,-105")
    coord.append("50,-100")
    coord.append("50,-95")
    coord.append("50,-90")
    coord.append("50,-85")
    coord.append("50,-80")
    coord.append("50,-75")
    coord.append("50,-70")
    coord.append("55,-120")
    coord.append("55,-115")
    coord.append("55,-110")
    coord.append("55,-105")
    coord.append("55,-100")
    coord.append("55,-95")
    coord.append("55,-90")
    coord.append("55,-85")
    coord.append("55,-80")
    coord.append("55,-75")
    coord.append("55,-70")
    for xy in coord:
        x = xy.split(",")[0]
        y = xy.split(",")[1]
        logger.info(("%s-%s..." % (x, y)))
        url = "https://z1-prod-cec-services-location.azurewebsites.net/api/cec/locations/search"
        payload = {"latitude": x, "longitude": y, "radius": "500"}
        r = session.post(url, headers=headers, data=json.dumps(payload))
        if r.encoding is None:
            r.encoding = "utf-8"
        for line in r.iter_lines(decode_unicode=True):
            if '"website":"' in line:
                items = line.split('"account_id":"')
                for item in items:
                    if "yelp_accuracy_score" in item:
                        store = item.split('"storeId":')[1].split(",")[0]
                        if store not in locs:
                            locs.append(store)
                            website = "chuckecheese.com"
                            add = item.split('"address":"')[1].split('"')[0]
                            country = "US"
                            city = item.split('"locality":"')[1].split('"')[0]
                            state = item.split('"region":"')[1].split('"')[0]
                            lat = item.split('"latitude":"')[1].split('"')[0]
                            lng = item.split('"longitude":"')[1].split('"')[0]
                            phone = item.split('"phone":"')[1].split('"')[0]
                            loc = item.split('"website":"')[1].split('"')[0]
                            zc = item.split('"postcode":"')[1].split('"')[0]
                            typ = "<MISSING>"
                            name = "Chuck E. Cheese " + city + ", " + state
                            hours = item.split('"store_hours":"')[1].split('"')[0]
                            hours = hours.replace("1,", "Mon: ")
                            hours = hours.replace(";2,", "; Tue: ")
                            hours = hours.replace(";3,", "; Wed: ")
                            hours = hours.replace(";4,", "; Thu: ")
                            hours = hours.replace(";5,", "; Fri: ")
                            hours = hours.replace(";6,", "; Sat: ")
                            hours = hours.replace(";7,", "; Sun: ")
                            hours = hours.replace(",", "-")
                            hours = hours[:-1]
                            if hours == "":
                                hours = "<MISSING>"
                            if "https://" not in loc:
                                loc = "https://" + loc
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

        logger.info(("Found %s Locations..." % str(len(locs))))

    urls = [
        "https://locations.chuckecheese.com/ca/ab",
        "https://locations.chuckecheese.com/ca/on",
    ]
    locs = [
        "https://locations.chuckecheese.com/ca/bc/langley/6339-200th-street",
        "https://locations.chuckecheese.com/ca/sk/regina/685-university-park-dr.",
    ]
    cities = []
    for url in urls:
        logger.info(url)
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '="Directory-listLink" href="../' in line:
                items = line.split('="Directory-listLink" href="../')
                for item in items:
                    if '"directorylink" data-count="(' in item:
                        lurl = (
                            "https://locations.chuckecheese.com/" + item.split('"')[0]
                        )
                        count = item.split('"directorylink" data-count="(')[1].split(
                            ")"
                        )[0]
                        if count == "1":
                            locs.append(lurl)
                        else:
                            cities.append(lurl)
    for city in cities:
        logger.info(city)
        r = session.get(city, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '"Teaser-link" href="../../' in line:
                items = line.split('"Teaser-link" href="../../')
                for item in items:
                    if 'data-ya-track="visitpage">' in item:
                        lurl = (
                            "https://locations.chuckecheese.com/" + item.split('"')[0]
                        )
                        locs.append(lurl)
    for loc in locs:
        website = "chuckecheese.com"
        country = "CA"
        typ = "<MISSING>"
        store = "<MISSING>"
        name = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        add = ""
        logger.info(loc)
        r = session.get(loc, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '<span class="c-address-city">' in line:
                city = line.split('<span class="c-address-city">')[1].split("<")[0]
                name = city
            if '<span class="c-address-state" >' in line:
                state = line.split('<span class="c-address-state" >')[1].split("<")[0]
            if add == "" and 'class="c-address-street-1">' in line:
                add = line.split('class="c-address-street-1">')[1].split("<")[0]
            if 'id="phone-main">' in line:
                phone = line.split('id="phone-main">')[1].split("<")[0]
            if 'itemprop="latitude" content="' in line:
                lat = line.split('itemprop="latitude" content="')[1].split('"')[0]
                lng = line.split('itemprop="longitude" content="')[1].split('"')[0]
            if 'itemprop="postalCode">' in line:
                zc = line.split('itemprop="postalCode">')[1].split("<")[0]
            if " data-days='[{" in line and hours == "":
                days = (
                    line.split(" data-days='[{")[1]
                    .split("]' data-utc")[0]
                    .split('"day":"')
                )
                for day in days:
                    if '"intervals"' in day:
                        if '"isClosed":false' not in day:
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
        if "0" not in hours:
            hours = "Temporarily Closed"
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
