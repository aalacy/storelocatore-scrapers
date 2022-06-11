import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("footlocker_co_uk")


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
    cities = []
    url = "https://stores.footlocker.co.uk/en/index.html"
    r = session.get(url, headers=headers)
    website = "footlocker.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'content-item-link" href="../' in line:
            items = line.split('content-item-link" href="../')
            for item in items:
                if '</a><span class="c-directory' in item:
                    lurl = "https://stores.footlocker.co.uk/" + item.split('"')[0]
                    if lurl.count("/") == 4:
                        cities.append(lurl)
                    else:
                        locs.append(lurl)
    for city in cities:
        logger.info(city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if (
                'LocationCard-caret fa fa-caret-right"></i></a></div></div><a href="../'
                in line2
            ):
                items = line2.split(
                    'LocationCard-caret fa fa-caret-right"></i></a></div></div><a href="../'
                )
                for item in items:
                    if 'data-ya-track="dir_visit_page"' in item:
                        locs.append(
                            "https://stores.footlocker.co.uk/" + item.split('"')[0]
                        )
    for loc in locs:
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
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("<")[0]
            if '"latitude" content="' in line2:
                lat = line2.split('"latitude" content="')[1].split('"')[0]
                lng = line2.split('"longitude" content="')[1].split('"')[0]
            if add == "" and '"c-address-street-1">' in line2:
                add = line2.split('"c-address-street-1">')[1].split("<")[0]
                city = line2.split('itemprop="addressLocality">')[1].split("<")[0]
                state = "<MISSING>"
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
                phone = line2.split('c-phone-main-number-link" href="tel:')[1].split(
                    '"'
                )[0]
            if '<td class="c-location-hours-details-row-day">' in line2:
                if 'row-intervals-instance-open">' not in line2:
                    hours = (
                        "Sun: "
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Sunday</td>'
                        )[1]
                        .split('intervals">')[1]
                        .split("<")[0]
                    )
                    hours = (
                        hours
                        + "; Mon: "
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Monday</td>'
                        )[1]
                        .split('intervals">')[1]
                        .split("<")[0]
                    )
                    hours = (
                        hours
                        + "; Tue: "
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Tuesday</td>'
                        )[1]
                        .split('intervals">')[1]
                        .split("<")[0]
                    )
                    hours = (
                        hours
                        + "; Wed: "
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Wednesday</td>'
                        )[1]
                        .split('intervals">')[1]
                        .split("<")[0]
                    )
                    hours = (
                        hours
                        + "; Thu: "
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Thursday</td>'
                        )[1]
                        .split('intervals">')[1]
                        .split("<")[0]
                    )
                    hours = (
                        hours
                        + "; Fri: "
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Friday</td>'
                        )[1]
                        .split('intervals">')[1]
                        .split("<")[0]
                    )
                    hours = (
                        hours
                        + "; Sat: "
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Saturday</td>'
                        )[1]
                        .split('intervals">')[1]
                        .split("<")[0]
                    )
                else:
                    hours = (
                        "Sun: "
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Sunday</td>'
                        )[1]
                        .split('intervals-instance-open">')[1]
                        .split("<")[0]
                        + "-"
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Sunday</td>'
                        )[1]
                        .split('intervals-instance-close">')[1]
                        .split("<")[0]
                    )
                    hours = (
                        hours
                        + "; Mon: "
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Monday</td>'
                        )[1]
                        .split('intervals-instance-open">')[1]
                        .split("<")[0]
                        + "-"
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Monday</td>'
                        )[1]
                        .split('intervals-instance-close">')[1]
                        .split("<")[0]
                    )
                    hours = (
                        hours
                        + "; Tue: "
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Tuesday</td>'
                        )[1]
                        .split('intervals-instance-open">')[1]
                        .split("<")[0]
                        + "-"
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Tuesday</td>'
                        )[1]
                        .split('intervals-instance-close">')[1]
                        .split("<")[0]
                    )
                    hours = (
                        hours
                        + "; Wed: "
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Wednesday</td>'
                        )[1]
                        .split('intervals-instance-open">')[1]
                        .split("<")[0]
                        + "-"
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Wednesday</td>'
                        )[1]
                        .split('intervals-instance-close">')[1]
                        .split("<")[0]
                    )
                    hours = (
                        hours
                        + "; Thu: "
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Thursday</td>'
                        )[1]
                        .split('intervals-instance-open">')[1]
                        .split("<")[0]
                        + "-"
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Thursday</td>'
                        )[1]
                        .split('intervals-instance-close">')[1]
                        .split("<")[0]
                    )
                    hours = (
                        hours
                        + "; Fri: "
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Friday</td>'
                        )[1]
                        .split('intervals-instance-open">')[1]
                        .split("<")[0]
                        + "-"
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Friday</td>'
                        )[1]
                        .split('intervals-instance-close">')[1]
                        .split("<")[0]
                    )
                    hours = (
                        hours
                        + "; Sat: "
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Saturday</td>'
                        )[1]
                        .split('intervals-instance-open">')[1]
                        .split("<")[0]
                        + "-"
                        + line2.split(
                            '<td class="c-location-hours-details-row-day">Saturday</td>'
                        )[1]
                        .split('intervals-instance-close">')[1]
                        .split("<")[0]
                    )
        name = name.replace("&amp;", "&").replace("&#39;", "'").replace("&amp", "&")
        add = add.replace("&amp;", "&").replace("&#39;", "'").replace("&amp", "&")
        if "(" in city:
            city = city.split("(")[0].strip()
        city = city.replace("&amp;", "&")
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
