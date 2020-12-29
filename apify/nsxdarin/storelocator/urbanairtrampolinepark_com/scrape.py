import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("urbanairtrampolinepark_com")


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
    url = "https://www.urbanairtrampolinepark.com/locations"
    r = session.get(url, headers=headers)
    website = "urbanairtrampolinepark.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            '<div class="location " data-link="https://www.urbanairtrampolinepark.com/locations/'
            in line
        ):
            items = line.split(
                '<div class="location " data-link="https://www.urbanairtrampolinepark.com/locations/'
            )
            for item in items:
                if 'data-title="' in item:
                    locs.append(
                        "https://www.urbanairtrampolinepark.com/locations/"
                        + item.split('"')[0]
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
            if '<div class="location-name"><h1>' in line2 and name == "":
                name = line2.split('<div class="location-name"><h1>')[1].split("<")[0]
            if '"latitude":"' in line2:
                if (
                    '"addressCountry":"United States"' in line2
                    or '"addressCountry":"Canada' in line2
                ):
                    lat = line2.split('"latitude":"')[1].split('"')[0]
                    lng = line2.split('"longitude":"')[1].split('"')[0]
                    phone = line2.split('telephone":"')[1].split('"')[0]
                    add = line2.split('"streetAddress":"')[1].split('"')[0]
                    city = line2.split('"addressLocality":"')[1].split('"')[0]
                    state = line2.split('"addressRegion":"')[1].split('"')[0]
                    zc = line2.split('"postalCode":"')[1].split('"')[0]
            if '<div class="time">' in line2:
                days = line2.split('<div class="time">')
                for day in days:
                    if "CONTACT US</a>" not in day:
                        hrs = (
                            day.split("</div>")[0]
                            .replace("<strong>", "")
                            .replace("</strong>", "")
                            .strip()
                            .replace("  ", " ")
                        )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        if '">;' in hours:
            hours = hours.split('">;')[1].strip()
        if add != "":
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
