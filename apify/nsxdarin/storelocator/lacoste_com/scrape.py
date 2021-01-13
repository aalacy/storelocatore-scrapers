import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("lacoste_com")


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
    url = "https://global.lacoste.com/us/stores/unitedstates"
    r = session.get(url, headers=headers)
    website = "lacoste.com"
    typ = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"name":"' in line:
            items = line.split('{"name":"')
            for item in items:
                if '"url":"/unitedstates/' in item:
                    locs.append(
                        "https://global.lacoste.com/us/stores?country=unitedstates&city="
                        + item.split('"url":"/unitedstates/')[1].split('"')[0]
                        + "&json=true"
                    )
    for loc in locs:
        logger.info(loc)
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '{"id":"' in line2:
                items = line2.split('{"id":"')
                for item in items:
                    if '"name":"' in item:
                        name = item.split('"name":"')[1].split('"')[0]
                        country = "US"
                        add = item.split('"address":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = "<MISSING>"
                        zc = item.split('"postalCode":"')[1].split('"')[0]
                        try:
                            phone = (
                                item.split('"phone":"')[1]
                                .split('"')[0]
                                .replace("+1", "")
                            )
                        except:
                            phone = "<MISSING>"
                        lat = item.split('"latitude":')[1].split(",")[0]
                        lng = item.split('"longitude":')[1].split(",")[0]
                        store = item.split('"')[0]
                        try:
                            hours = item.split('"hours":"')[1].split('"')[0]
                            hours = (
                                hours.replace("1-6", "Mon-Sat: ")
                                .replace("7:", "Sun: ")
                                .replace(",", "; ")
                            )
                            hours = hours.replace("1-Sun", "Mon-Sun").replace(
                                ": :", ":"
                            )
                            hours = hours.replace("6-Sun", "Sat-Sun").replace(
                                "6:", "Sat:"
                            )
                        except:
                            hours = "<MISSING>"
                        lurl = (
                            "https://global.lacoste.com/us/stores"
                            + item.split('"url":"')[1].split('"')[0]
                        )
                        name = (
                            name.replace("&#39;", "'")
                            .replace("&amp;", "&")
                            .replace("&#35;", "#")
                        )
                        add = (
                            add.replace("&#39;", "'")
                            .replace("&amp;", "&")
                            .replace("&#35;", "#")
                        )
                        hours = (
                            hours.replace("5:", "Fri:")
                            .replace("1-", "Mon-")
                            .replace("4-", "Thu-")
                            .replace("3:", "Wed:")
                        )
                        hours = (
                            hours.replace("1:", "Mon:")
                            .replace("2:", "Tue:")
                            .replace("3:", "Wed:")
                        )
                        hours = (
                            hours.replace("4:", "Thu:")
                            .replace("5-", "Fri-")
                            .replace("3-", "Wed-")
                            .replace("2-", "Tue-")
                        )
                        if "closed" not in lurl:
                            yield [
                                website,
                                lurl,
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
    locs = []
    url = "https://global.lacoste.com/us/stores/canada"
    r = session.get(url, headers=headers)
    website = "lacoste.com"
    typ = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"name":"' in line:
            items = line.split('{"name":"')
            for item in items:
                if '"url":"/canada/' in item:
                    locs.append(
                        "https://global.lacoste.com/us/stores?country=canada&city="
                        + item.split('"url":"/canada/')[1].split('"')[0]
                        + "&json=true"
                    )
    for loc in locs:
        logger.info(loc)
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '{"id":"' in line2:
                items = line2.split('{"id":"')
                for item in items:
                    if '"name":"' in item:
                        name = item.split('"name":"')[1].split('"')[0]
                        country = "CA"
                        add = item.split('"address":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = "<MISSING>"
                        zc = item.split('"postalCode":"')[1].split('"')[0]
                        try:
                            phone = (
                                item.split('"phone":"')[1]
                                .split('"')[0]
                                .replace("+1", "")
                            )
                        except:
                            phone = "<MISSING>"
                        lat = item.split('"latitude":')[1].split(",")[0]
                        lng = item.split('"longitude":')[1].split(",")[0]
                        store = item.split('"')[0]
                        try:
                            hours = item.split('"hours":"')[1].split('"')[0]
                            hours = (
                                hours.replace("1-6", "Mon-Sat: ")
                                .replace("7:", "Sun: ")
                                .replace(",", "; ")
                            )
                            hours = hours.replace("1-Sun", "Mon-Sun").replace(
                                ": :", ":"
                            )
                            hours = hours.replace("6-Sun", "Sat-Sun").replace(
                                "6:", "Sat:"
                            )
                        except:
                            hours = "<MISSING>"
                        lurl = (
                            "https://global.lacoste.com/us/stores"
                            + item.split('"url":"')[1].split('"')[0]
                        )
                        name = (
                            name.replace("&#39;", "'")
                            .replace("&amp;", "&")
                            .replace("&#35;", "#")
                        )
                        add = (
                            add.replace("&#39;", "'")
                            .replace("&amp;", "&")
                            .replace("&#35;", "#")
                        )
                        hours = (
                            hours.replace("5:", "Fri:")
                            .replace("1-", "Mon-")
                            .replace("4-", "Thu-")
                            .replace("3:", "Wed:")
                        )
                        hours = (
                            hours.replace("1:", "Mon:")
                            .replace("2:", "Tue:")
                            .replace("3:", "Wed:")
                        )
                        hours = (
                            hours.replace("4:", "Thu:")
                            .replace("5-", "Fri-")
                            .replace("3-", "Wed-")
                            .replace("2-", "Tue-")
                        )
                        if "closed" not in lurl:
                            yield [
                                website,
                                lurl,
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
