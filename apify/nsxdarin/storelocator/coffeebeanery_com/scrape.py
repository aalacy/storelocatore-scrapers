import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("coffeebeanery_com")


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
    url = "https://www.coffeebeanery.com/tools/store-locator"
    r = session.get(url, headers=headers)
    website = "coffeebeanery.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "-black.png\")'  onmouseover='hoverStart(" in line:
            items = line.split("onmouseover='hoverStart(")
            for item in items:
                if "div class='distance'>" in item:
                    locs.append(
                        "https://stores.boldapps.net/front-end/get_store_info.php?shop=coffee-beanery1.myshopify.com&data=detailed&store_id="
                        + item.split(")")[0]
                    )
    for loc in locs:
        logger.info(loc)
        lurl = "<MISSING>"
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.rsplit("=", 1)[1]
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<span class='name'>" in line2:
                name = line2.split("<span class='name'>")[1].split("<")[0].strip()
                add = line2.split("<span class='address'>")[1].split("<")[0].strip()
                city = line2.split("<span class='city'>")[1].split("<")[0].strip()
                try:
                    add = (
                        add
                        + " "
                        + line2.split("<span class='address2'>")[1]
                        .split("<")[0]
                        .strip()
                    )
                    add = add.strip()
                except:
                    pass
                state = (
                    line2.split("<span class='prov_state'>")[1].split("<")[0].strip()
                )
                try:
                    zc = (
                        line2.split("<span class='postal_zip'>")[1]
                        .split("<")[0]
                        .strip()
                    )
                except:
                    zc = "<MISSING>"
                try:
                    phone = line2.split("<span class='phone'>")[1].split("<")[0].strip()
                except:
                    phone = "<MISSING>"
                try:
                    lurl = (
                        line2.split("Website: <\\/span><a href='")[1]
                        .split("'")[0]
                        .replace("\\", "")
                    )
                except:
                    pass
                try:
                    hours = (
                        line2.split("<span class='hours'>")[1]
                        .split("<\\/span>")[0]
                        .replace("<br \\/>", "; ")
                    )
                except:
                    hours = "<MISSING>"
            if "<span class='country'> Guam" in line2:
                state = "Guam"
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
