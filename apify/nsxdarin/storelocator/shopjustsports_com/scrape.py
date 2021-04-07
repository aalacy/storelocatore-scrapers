import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("shopjustsports_com")


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
    url = "https://www.shopjustsports.com/apps/store-locator"
    r = session.get(url, headers=headers)
    website = "shopjustsports.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "markersCoords.push(" in line and len(locs) < 1:
            items = line.split("{lat:")
            for item in items:
                if "id:" in item:
                    llat = item.split(",")[0].strip()
                    llng = item.split(" lng: ")[1].split(",")[0]
                    lid = item.split("id:")[1].split(",")[0]
                    locs.append(
                        "https://stores.boldapps.net/front-end/get_store_info.php?shop=just-sports-arizona.myshopify.com&data=detailed&store_id="
                        + lid
                        + "|"
                        + llat
                        + "|"
                        + llng
                    )
    for loc in locs:
        locurl = loc.split("|")[0]
        logger.info(locurl)
        lurl = "https://www.shopjustsports.com/apps/store-locator"
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = locurl.rsplit("id=", 1)[1]
        phone = ""
        lat = loc.split("|")[1]
        lng = loc.split("|")[2]
        hours = ""
        r2 = session.get(locurl, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '{"data":"' in line2:
                name = line2.split("<span class='name'>")[1].split("<")[0].strip()
                add = line2.split("<span class='address'>")[1].split("<")[0].strip()
                city = line2.split("<span class='city'>")[1].split("<")[0].strip()
                state = (
                    line2.split("<span class='prov_state'>")[1].split("<")[0].strip()
                )
                zc = line2.split("<span class='postal_zip'>")[1].split("<")[0].strip()
                phone = line2.split("<span class='phone'>")[1].split("<")[0].strip()
                hours = (
                    line2.split("<span class='hours'>")[1].split("<\\/span>")[0].strip()
                )
                hours = hours.replace("<br \\/>", "; ")
                if "HOURS<br \\/>Monday" in hours:
                    hours = hours.split("HOURS<br \\/>")[1]
        hours = hours.replace("LIMITED STORE HOURS; ", "")
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
