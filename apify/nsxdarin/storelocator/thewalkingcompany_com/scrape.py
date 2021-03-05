import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("thewalkingcompany_com")


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
    coords = []
    url = "https://www.thewalkingcompany.com/apps/store-locator"
    r = session.get(url, headers=headers)
    website = "thewalkingcompany.com"
    country = "US"
    loc = "<MISSING>"
    typ = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "markersCoords.push({lat:" in line:
            items = line.split("markersCoords.push({lat:")
            for item in items:
                if ", lng:" in item:
                    mid = item.split("id:")[1].split(",")[0]
                    mlat = item.split(",")[0].strip()
                    mlng = item.split("lng:")[1].split(",")[0].strip()
                    coords.append(mid + "|" + mlat + "|" + mlng)
        if "<span class='name'>" in line:
            items = line.split("onmouseover='hoverStart(")
            for item in items:
                if "<span class='address'>" in item:
                    name = item.split("<span class='name'>")[1].split("<")[0].strip()
                    store = item.split(")")[0]
                    add = item.split("<span class='address'>")[1].split("<")[0].strip()
                    city = item.split("<span class='city'>")[1].split("<")[0].strip()
                    state = (
                        item.split("<span class='prov_state'>")[1].split("<")[0].strip()
                    )
                    zc = (
                        item.split("<span class='postal_zip'>")[1].split("<")[0].strip()
                    )
                    phone = item.split("<span class='phone'>")[1].split("<")[0].strip()
                    hurl = (
                        "https://stores.boldapps.net/front-end/get_store_info.php?shop=walkingco.myshopify.com&data=detailed&store_id="
                        + store
                    )
                    r2 = session.get(hurl, headers=headers)
                    hours = ""
                    for line2 in r2.iter_lines():
                        line2 = str(line2.decode("utf-8"))
                        if "<span class='hours'>" in line2:
                            hours = line2.split("<span class='hours'>")[1].split(
                                "<\\/span>"
                            )[0]
                            hours = hours.replace("<br>", "; ")
                    for coord in coords:
                        if store == coord.split("|")[0]:
                            lat = coord.split("|")[1]
                            lng = coord.split("|")[2]
                    if "Temporarily" in hours:
                        hours = "Temporarily Closed"
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
