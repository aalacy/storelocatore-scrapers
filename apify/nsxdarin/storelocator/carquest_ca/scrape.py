import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("carquest_ca")

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
    urls = ["https://www.carquest.com/stores/canada"]
    states = []
    cities = []
    locs = []
    allstores = []
    website = "carquest.ca"
    typ = "<MISSING>"
    country = "<MISSING>"
    for url in urls:
        r = session.get(url, headers=headers)
        if r.encoding is None:
            r.encoding = "utf-8"
        for line in r.iter_lines(decode_unicode=True):
            if '<a class="Directory-listLink" href="../' in line:
                items = line.split('<a class="Directory-listLink" href="../')
                for item in items:
                    if 'data-ya-track="todirectory"' in item:
                        count = item.split('data-count="(')[1].split(")")[0]
                        if count != "1":
                            states.append(
                                "https://www.carquest.com/"
                                + item.split('"')[0].replace("..", "")
                            )
                        else:
                            locs.append(
                                "https://www.carquest.com/"
                                + item.split('"')[0]
                                .replace("..", "")
                                .replace("&#39;", "'")
                            )
    for state in states:
        logger.info(("Pulling State %s..." % state))
        r = session.get(state, headers=headers)
        if r.encoding is None:
            r.encoding = "utf-8"
        for line in r.iter_lines(decode_unicode=True):
            if '<a class="Directory-listLink" href="' in line:
                items = line.split('<a class="Directory-listLink" href="')
                for item in items:
                    if 'data-ya-track="todirectory"' in item:
                        count = item.split('data-count="(')[1].split(")")[0]
                        if count != "1":
                            cities.append(
                                "https://www.carquest.com/"
                                + item.split('"')[0].replace("..", "")
                            )
                        else:
                            locs.append(
                                "https://www.carquest.com/"
                                + item.split('"')[0]
                                .replace("..", "")
                                .replace("&#39;", "'")
                            )
    for city in cities:
        logger.info(("Pulling City %s..." % city))
        typ = "Carquest"
        r = session.get(city, headers=headers)
        if r.encoding is None:
            r.encoding = "utf-8"
        for line in r.iter_lines(decode_unicode=True):
            if 'data-ya-track="page" href="..' in line:
                items = line.split('data-ya-track="page" href="..')
                for item in items:
                    if "Store Details" in item:
                        locs.append(
                            "https://www.carquest.com/"
                            + item.split('"')[0].replace("&#39;", "'")
                        )
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        typ = "Carquest"
        r = session.get(loc, headers=headers)
        if r.encoding is None:
            r.encoding = "utf-8"
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        lat = ""
        lng = ""
        hours = ""
        country = "CA"
        phone = ""
        store = ""
        for line in r.iter_lines(decode_unicode=True):
            if '"store_id":"' in line:
                store = line.split('"store_id":"')[1].split('"')[0]
            if '"page_name":"' in line:
                name = line.split('"page_name":"')[1].split('"')[0]
                city = line.split(',"store_city":"')[1].split('"')[0]
                state = line.split('"store_state":"')[1].split('"')[0]
                zc = line.split('"store_zip":"')[1].split('"')[0]
            if '"line1":"' in line:
                add = line.split('"line1":"')[1].split('"')[0]
                try:
                    add = add + " " + line.split('"line2":"')[1].split('"')[0]
                    add = add.strip()
                except:
                    pass
            if 'id="phone-main">' in line:
                phone = line.split('id="phone-main">')[1].split("<")[0]
            if '<meta itemprop="latitude" content="' in line:
                lat = line.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                lng = line.split('<meta itemprop="longitude" content="')[1].split('"')[
                    0
                ]
            if '{"day":"MONDAY"' in line:
                try:
                    if (
                        '"isClosed":true'
                        in line.split('"day":"SUNDAY"')[1].split("}")[0]
                    ):
                        hours = "Sun: Closed"
                    else:
                        hours = (
                            "Sun: "
                            + line.split('"day":"SUNDAY"')[1]
                            .split('"start":')[1]
                            .split("}")[0]
                            + "AM-"
                            + line.split('"day":"SUNDAY"')[1]
                            .split('"end":')[1]
                            .split(",")[0]
                            + "PM"
                        )
                    hours = (
                        hours
                        + "; "
                        + "Mon: "
                        + line.split('{"day":"MONDAY"')[1]
                        .split('"start":')[1]
                        .split("}")[0]
                        + "AM-"
                        + line.split('{"day":"MONDAY"')[1]
                        .split('{"end":')[1]
                        .split(",")[0]
                        + "PM"
                    )
                    hours = (
                        hours
                        + "; "
                        + "Tue: "
                        + line.split('{"day":"TUESDAY"')[1]
                        .split('"start":')[1]
                        .split("}")[0]
                        + "AM-"
                        + line.split('{"day":"TUESDAY"')[1]
                        .split('{"end":')[1]
                        .split(",")[0]
                        + "PM"
                    )
                    hours = (
                        hours
                        + "; "
                        + "Wed: "
                        + line.split('{"day":"WEDNESDAY"')[1]
                        .split('"start":')[1]
                        .split("}")[0]
                        + "AM-"
                        + line.split('{"day":"WEDNESDAY"')[1]
                        .split('{"end":')[1]
                        .split(",")[0]
                        + "PM"
                    )
                    hours = (
                        hours
                        + "; "
                        + "Thu: "
                        + line.split('{"day":"THURSDAY"')[1]
                        .split('"start":')[1]
                        .split("}")[0]
                        + "AM-"
                        + line.split('{"day":"THURSDAY"')[1]
                        .split('{"end":')[1]
                        .split(",")[0]
                        + "PM"
                    )
                    hours = (
                        hours
                        + "; "
                        + "Fri: "
                        + line.split('{"day":"FRIDAY"')[1]
                        .split('"start":')[1]
                        .split("}")[0]
                        + "AM-"
                        + line.split('{"day":"FRIDAY"')[1]
                        .split('{"end":')[1]
                        .split(",")[0]
                        + "PM"
                    )
                    hours = (
                        hours
                        + "; "
                        + "Sat: "
                        + line.split('{"day":"SATURDAY"')[1]
                        .split('"start":')[1]
                        .split("}")[0]
                        + "AM-"
                        + line.split('{"day":"SATURDAY"')[1]
                        .split('{"end":')[1]
                        .split(",")[0]
                        + "PM"
                    )
                except:
                    hours = "Sun-Sat: Closed"
        if store not in allstores:
            allstores.append(store)
            if state == "":
                state = "PR"
            name = name.replace("\\u0026#39;", "'")
            hours = (
                hours.replace("00", ":00")
                .replace("30", ":30")
                .replace("1:000AM", "10:00AM")
                .replace("2:000PM", "20:00PM")
            )
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
