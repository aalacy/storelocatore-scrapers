import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("applebeescanada_com")


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
    url = "https://applebeescanada.com/locations/"
    r = session.get(url, headers=headers)
    website = "applebeescanada.com"
    typ = "<MISSING>"
    country = "CA"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"tb-button__link" href="https://applebeescanada.com/location/' in line:
            locs.append(line.split('"tb-button__link" href="')[1].split('"')[0])
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
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<h1 class="tb-heading has-text-color"' in line2:
                name = (
                    line2.split('<h1 class="tb-heading has-text-color"')[1]
                    .split('">')[1]
                    .split("<")[0]
                    .replace("&#8217;", "'")
                    .replace("&#8211;", "-")
                )
            if (
                '<div class="tb-field" data-toolset-blocks-field="' in line2
                and add == ""
            ):
                addinfo = (
                    line2.split('<div class="tb-field" data-toolset-blocks-field="')[1]
                    .split('">')[1]
                    .split("<")[0]
                )
                addinfo = addinfo.replace("Falls ON", "Falls, ON")
                addinfo = addinfo.replace("Canada", "").replace("  ", " ")
                addinfo = addinfo.replace("ON,", "ON")
                if "388 Country Hills Blvd" in addinfo:
                    add = "388 Country Hills Blvd NE #707"
                    city = "Calgary"
                    state = "AB"
                    zc = "T3K 5J6"
                else:
                    add = addinfo.split(",")[0].strip()
                    city = addinfo.split(",")[1].strip()
                    state = addinfo.split(",")[2].strip().split(" ")[0]
                    zc = addinfo.split(",")[2].strip().split(" ", 1)[1]
                if add == "Regina":
                    state = "SK"
                    city = "Regina"
                    add = addinfo.split(",")[1].strip()
                    zc = addinfo.split(",")[2].strip()
                if add == "Thunder Bay":
                    state = "ON"
                    city = "Thunder Bay"
                    add = addinfo.split(",")[1].strip()
                    zc = addinfo.split(",")[2].strip()
                if add == "Niagara Falls":
                    state = "ON"
                    city = "Niagara Falls"
                    add = addinfo.split(",")[1].strip()
                    zc = addinfo.split(",")[2].strip()
                if add == "Winnipeg":
                    city = "Winnipeg"
                    state = "MB"
                    add = addinfo.split(",")[1].strip()
                    zc = addinfo.split(",")[2].strip()
                if add == "Brandon":
                    city = "Brandon"
                    state = "MB"
                    add = addinfo.split(",")[1].strip()
                    zc = addinfo.split(",")[2].strip()
                if add == "Ajax":
                    city = "Ajax"
                    state = "ON"
                    add = addinfo.split(",")[1].strip()
                    zc = addinfo.split(",")[2].strip()
            if "Call:</strong>&nbsp;&nbsp;" in line2:
                phone = line2.split("Call:</strong>&nbsp;&nbsp;")[1].split("<")[0]
            if 'data-markerlat="' in line2:
                lat = line2.split('data-markerlat="')[1].split('"')[0]
                lng = line2.split('data-markerlon="')[1].split('"')[0]
            if "day<br />" in line2 or "Week<" in line2:
                if '"tb-field"' in line2:
                    HFound = True
                    hours = line2.split("<p>")[1].split("<")[0] + ": "
            if HFound and "</div>" in line2:
                HFound = False
            if HFound and '"tb-field"' not in line2:
                if "<br />" in line2:
                    hours = hours + "; " + line2.split(">")[1].split("<")[0]
                else:
                    hours = hours + ": " + line2.split("<")[0]
        if hours == "":
            hours = "<MISSING>"
        hours = hours.replace(": :", ":")
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
