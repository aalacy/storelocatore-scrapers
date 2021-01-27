import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("ourcoop_com")


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
    url = "https://www.ourcoop.com/locations"
    r = session.get(url, headers=headers)
    website = "ourcoop.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a class="get-directions-link showDetail" href="' in line:
            lurl = "https://www.ourcoop.com" + line.split('href="')[1].split('"')[0]
            locs.append(lurl)
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
        HFound = False
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<h2>" in line2:
                name = line2.split("<h2>")[1].split("<")[0]
                if " - " in name:
                    name = name.split(" -")[0]
            if (
                '<span class="fa fa-location-pin m-location-info__icon"></span>'
                in line2
            ):
                add = line2.split(
                    '<span class="fa fa-location-pin m-location-info__icon"></span>'
                )[1].split("<")[0]
                addinfo = line2.split("<br/>")[1].split("<")[0].strip()
                city = addinfo.split(",")[0]
                state = addinfo.split(",")[1].strip().split(" ")[0]
                zc = addinfo.rsplit(" ", 1)[1]
            if 'icon-label" href="tel:' in line2:
                phone = line2.split('icon-label" href="tel:')[1].split('"')[0]
            if ".setView([" in line2:
                lat = line2.split(".setView([")[1].split(",")[0]
                lng = line2.split(".setView([")[1].split(",")[1].strip().split("]")[0]
            if 'info__hours">' in line2:
                HFound = True
                hours = (
                    line2.split('info__hours">')[1]
                    .replace("\t", "")
                    .replace("\r", "")
                    .replace("\n", "")
                    .strip()
                )
            if HFound and "</p>" in line2:
                hours = hours + line2.split("<")[0]
                HFound = False
            if HFound and 'info__hours">' not in line2:
                if "day" in line2:
                    hours = (
                        hours
                        + "; "
                        + line2.replace("\t", "")
                        .replace("\r", "")
                        .replace("\n", "")
                        .strip()
                    )
                else:
                    hours = hours + ": " + line2.split("<")[0]
        hours = hours.replace("day", "day:").replace("::", "")
        if "Bedford Moore Farmers" in name:
            name = "Bedford Moore Farmers"
        if "Guntown" in loc:
            hours = "Monday - Friday 7:30 a.m. - 4:30 p.m."
        if "Weakley-Farmers-Greenfield" in loc:
            hours = "Monday - Friday 7:30 am - 4:30 pm; Saturday 7:30 am - 12:00 pm"
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
