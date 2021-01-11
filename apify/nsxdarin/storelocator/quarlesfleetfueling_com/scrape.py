import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
}

logger = SgLogSetup().get_logger("quarlesfleetfueling_com")


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
    url = (
        "https://www.quarlesinc.com/fleet-fueling-products/quarles-fleet-fueling-sites/"
    )
    nid = ""
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"quarles_locator_nonce":"' in line:
            nid = line.split('"quarles_locator_nonce":"')[1].split('"')[0]
    url = "https://www.quarlesinc.com/wp-admin/admin-ajax.php"
    payload = {
        "action": "quarles_locator_ajax",
        "quarles_locator_nonce": nid,
        "location[lat]": "40.00",
        "location[long]": "-75.00",
        "location[distance]": "4000",
        "location[value]": "",
    }
    r = session.post(url, headers=headers, data=payload)
    website = "quarlesfleetfueling.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    hours = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<li class='row' data-lat='" in line:
            lat = line.split("<li class='row' data-lat='")[1].split("'")[0]
            lng = line.split("data-long='")[1].split("'")[0]
            store = line.split("data-site='")[1].split("'")[0]
        if "<h5>" in line:
            name = line.split("<h5>")[1].split("<")[0]
        if "<p class='address1'>" in line:
            add = line.split("<p class='address1'>")[1].split("<")[0]
        if "<p class='address2'>" in line:
            addinfo = line.split("<p class='address2'>")[1].split("<")[0]
            city = addinfo.split(",")[0]
            state = addinfo.split(",")[1].strip().split(" ")[0]
            zc = addinfo.split(",")[1].strip().split("<")[0].rsplit(" ", 1)[1]
            phone = "<MISSING>"
        if "<p class='do-not-print'>DISTANCE</p>" in line:
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
