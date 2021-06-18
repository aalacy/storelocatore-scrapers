import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("timhortons_co_uk")


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
    url = "https://timhortons.co.uk/find-a-tims"
    r = session.get(url, headers=headers)
    website = "timhortons.co.uk"
    typ = "<MISSING>"
    country = "GB"
    state = "<MISSING>"
    loc = "<MISSING>"
    store = "<MISSING>"
    logger.info("Pulling Stores")
    lines = r.iter_lines()
    for line in lines:
        line = str(line.decode("utf-8"))
        if "Hours: " in line:
            hours = (
                line.split("Hours: ", 1)[1]
                .strip()
                .replace("\r", "")
                .replace("\n", "")
                .replace("\t", "")
            )
            HFound = True
            while HFound:
                HFound = False
                g = next(lines)
                g = str(g.decode("utf-8"))
                if "pm" in g:
                    hours = (
                        hours
                        + "; "
                        + g.strip()
                        .replace("\r", "")
                        .replace("\n", "")
                        .replace("\t", "")
                    )
                    HFound = True
        if '<span class="location-city">' in line:
            name = line.split('<span class="location-city">')[1].split("<")[0]
        if 'data-module-lat="' in line:
            lat = line.split('data-module-lat="')[1].split('"')[0]
            lng = line.split('-lng="')[1].split('"')[0]
        if '<p class="location-address">' in line:
            g = next(lines)
            g = str(g.decode("utf-8"))
            add = ""
            addinfo = (
                g.strip()
                .replace("\t", "")
                .replace("\n", "")
                .replace("\r", "")
                .replace("<br/><br/>", "")
            )
            if "<br/>" not in addinfo:
                add = addinfo.split(",")[0]
                city = "<MISSING>"
                zc = addinfo.rsplit(",", 1)[1].strip()
            if add == "":
                if addinfo.count("<br/>") == 2:
                    add = addinfo.split("<br/>")[0] + " " + addinfo.split("<br/>")[1]
                    city = addinfo.split("<br/>")[2].split(",")[0]
                    zc = addinfo.rsplit(",", 1)[1].strip()
                else:
                    add = addinfo.split("<br/>")[0]
                    city = addinfo.split("<br/>")[1].split(",")[0]
                    zc = addinfo.rsplit(",", 1)[1].strip()
        if "COMING SOON" in line and "<!--p" not in line:
            name = name + " - COMING SOON"
        if '<div class="location-delivery-partners">' in line:
            phone = "<MISSING>"
            hours = hours.replace("&nbsp;", " ")
            if "<br/>" in hours:
                hours = hours.split("<br/>")[0]
            if "44 Winchester" in add:
                hours = "MON-SUN: 6am-12am"
            if "Unit 2 Queensgate Centre" in add:
                hours = "MON-SUN: 6am-midnight"
            hours = hours.replace("; <!--", "").replace("-->;", "").strip()
            if hours == "":
                hours = "<MISSING>"
            if "COMING SOON" not in name:
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
