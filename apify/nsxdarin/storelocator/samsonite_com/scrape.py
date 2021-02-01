import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import time

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("samsonite_com")


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
    ids = []
    url = "https://shop.samsonite.com/store-locator"
    r = session.get(url, headers=headers)
    website = "samsonite.com"
    typ = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            'option class="select-option" label="' in line
            and "Select<" not in line
            and ">Armed Forces" not in line
        ):
            state = line.split('value="')[1].split('"')[0]
            locs.append(
                "https://shop.samsonite.com/on/demandware.store/Sites-samsonite-Site/default/Stores-SearchByState?format=ajax&countryCode=US&distanceUnit=mi&maxResults=10000&maxdistance=30&stateCode="
                + state
                + "&dwfrm_storelocator_address_states_stateUS="
                + state
            )
    for loc in locs:
        logger.info(loc)
        time.sleep(5)
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"storeid": "' in line2:
                store = line2.split('"storeid": "')[1].split('"')[0]
                loc = (
                    "https://shop.samsonite.com/on/demandware.store/Sites-samsonite-Site/default/Stores-Details?StoreID="
                    + store
                )
            if '"name": "' in line2:
                name = line2.split('"name": "')[1].split('"')[0]
            if '"address1": "' in line2:
                add = line2.split('"address1": "')[1].split('"')[0]
            if '"address2": "' in line2:
                add = add + " " + line2.split('"address2": "')[1].split('"')[0]
                add = add.strip()
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"city": "' in line2:
                city = line2.split('"city": "')[1].split('"')[0]
            if '"stateCode": "' in line2:
                state = line2.split('"stateCode": "')[1].split('"')[0]
            if '"countryCode": "' in line2:
                country = line2.split('"countryCode": "')[1].split('"')[0]
            if '"phone": "' in line2:
                phone = line2.split('"phone": "')[1].split('"')[0]
                if phone == "":
                    phone = "<MISSING>"
            if 'storeHours": "' in line2:
                hours = line2.split('storeHours": "')[1].split('",')[0]
                hours = (
                    hours.replace("\\n", "")
                    .replace("\\t", "")
                    .replace("</li><li>", "; ")
                    .replace(
                        '<ul style=\\"font-family:Muli;\\"><li style=\\"color:green; font-family:\\"Muli\\";\\">',
                        "",
                    )
                )
                hours = hours.replace("</ul>", "")
                if hours == "":
                    hours = "<MISSING>"
            if '"latitude": "' in line2:
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line2:
                lng = line2.split('"longitude": "')[1].split('"')[0]
            if '"storeType": "' in line2:
                typ = line2.split('"storeType": "')[1].split('"')[0]
            if "}" in line2:
                if store not in ids:
                    ids.append(store)
                    if "Outlet" in name:
                        typ = "Outlet"
                    if typ == "":
                        typ = "<MISSING>"
                    hours = hours.replace('<li style=\\""color:red;\\"">', "")
                    hours = hours.replace("</li>", "")
                    if "Commons," in add:
                        add = add.split("Commons,")[1].strip()
                    if "Promenade," in add:
                        add = add.split("Promenade,")[1].strip()
                    if "Fultondale," in add:
                        add = add.split("Fultondale,")[1].strip()
                    if "Galleria," in add:
                        add = add.split("Galleria,")[1].strip()
                    if "Outlets -" in add:
                        add = add.split("Outlets -")[1].strip()
                    hours = hours.replace("Opened with Reduced Hours", "").strip()
                    if "Temporarily Closed" in hours:
                        hours = "Temporarily Closed"
                    if "Permanently" not in hours:
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
