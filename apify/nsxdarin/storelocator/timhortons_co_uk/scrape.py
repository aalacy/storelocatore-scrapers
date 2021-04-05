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
    url = "https://timhortons.co.uk/find-a-tims.php"
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
        if '<span class="location-city">' in line:
            name = line.split('<span class="location-city">')[1].split("<")[0]
        if 'data-module-lat="' in line:
            lat = line.split('data-module-lat="')[1].split('"')[0]
            lng = line.split('-lng="')[1].split('"')[0]
        if '<p class="location-address">' in line:
            g = next(lines)
            g = str(g.decode("utf-8"))
            if "CLOSED" in g:
                hours = "TEMPORARILY CLOSED"
            else:
                try:
                    hours = g.split("Hours: ")[1].split("<")[0]
                except:
                    hours = "<MISSING>"
            if "<br>Hours:" in g:
                addinfo = g.split("<br>Hours:")[0].strip().replace("\t", "")
            else:
                addinfo = g.rsplit("<br>", 1)[0].strip().replace("\t", "")
            if addinfo.count("<br>") == 2:
                add = addinfo.split("<br>")[0] + " " + addinfo.split("<br>")[1]
                city = addinfo.split("<br>")[2].split(",")[0]
                zc = addinfo.rsplit(",", 1)[1].strip()
            else:
                add = addinfo.split("<br>")[0]
                city = addinfo.split("<br>")[1].split(",")[0]
                zc = addinfo.rsplit(",", 1)[1].strip()
        if "COMING SOON" in line:
            name = name + " - COMING SOON"
        if '<div class="location-delivery-partners">' in line:
            phone = "<MISSING>"
            hours = hours.replace("&nbsp;", " ")
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
