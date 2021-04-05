import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("northerntool_com")


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
    url = "https://www.northerntool.com/stores/"
    r = session.get(url, headers=headers)
    website = "northerntool.com"
    typ = "<MISSING>"
    country = "US"
    states = []
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<option value="/stores/' in line:
            states.append(
                "https://www.northerntool.com" + line.split('value="')[1].split('"')[0]
            )
    for state in states:
        logger.info(state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if (
                '<p class="heading" style="font-size:14px; margin-bottom:10px;"><a href="'
                in line2
            ):
                locs.append(
                    "https://www.northerntool.com/stores/"
                    + line2.split(
                        '<p class="heading" style="font-size:14px; margin-bottom:10px;"><a href="'
                    )[1].split('"')[0]
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
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" |")[0]
            if "<address>" in line2:
                add = line2.split("<address>")[1].split("<")[0]
                g = next(lines)
                g = str(g.decode("utf-8"))
                addinfo = (
                    g.strip().replace("\t", "").replace("\r", "").replace("\n", "")
                )
                zc = addinfo.rsplit(" ", 1)[1]
                city = addinfo.split(",")[0]
                state = addinfo.split(",")[1].strip().split(" ")[0]
            if ">Phone:</b> " in line2:
                phone = line2.split(">Phone:</b> ")[1].split("<")[0]
            if '<dd class="' in line2:
                hrs = (
                    line2.split('<dd class="')[1].split('"')[0].title()
                    + ": "
                    + line2.split('">')[1].split("<")[0]
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if 'coords:"' in line2:
                lat = line2.split('coords:"')[1].split(",")[0]
                lng = line2.split(",")[1].split('"')[0].strip()
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
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
