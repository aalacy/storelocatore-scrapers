import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import usaddress

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("gpminvestments_com__breadbox")


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
    url = "https://gpminvestments.com/store-locator/"
    r = session.get(url, headers=headers)
    website = "gpminvestments.com/breadbox"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    hours = "<MISSING>"
    phone = "<MISSING>"
    add = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zc = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"marker_id":"' in line:
            items = line.split('"marker_id":"')
            for item in items:
                if '"title":"' in item:
                    add = ""
                    city = ""
                    state = ""
                    zc = ""
                    rawadd = ""
                    store = item.split('"')[0]
                    rawadd = item.split(',"address":"')[1].split('"')[0]
                    rawadd = rawadd.replace(",", "").replace("\\t", " ")
                    name = item.split('"title":"')[1].split('"')[0].replace("\\t", "")
                    lat = item.split('"lat":"')[1].split('"')[0]
                    lng = item.split('"lng":"')[1].split('"')[0]
                    if (
                        "3016 North John B Dennis" not in rawadd
                        and "5010 S Highway 69" not in rawadd
                        and "881 Windham Rd. S." not in rawadd
                        and "1101 3rd Ave. S." not in rawadd
                        and "4530 Tynecastle Highway" not in rawadd
                    ):
                        try:
                            add = usaddress.tag(rawadd)
                            try:
                                address = (
                                    add[0]["AddressNumber"]
                                    + " "
                                    + add[0]["StreetName"]
                                    + " "
                                    + add[0]["StreetNamePostType"]
                                )
                            except:
                                add = "<INACCESSIBLE>"
                            if add == "":
                                address = "<INACCESSIBLE>"
                            try:
                                city = add[0]["PlaceName"]
                            except:
                                city = "<INACCESSIBLE>"
                            try:
                                state = add[0]["StateName"]
                            except:
                                state = "<INACCESSIBLE>"
                            try:
                                zc = add[0]["ZipCode"]
                            except:
                                zc = "<INACCESSIBLE>"
                        except:
                            add = "<INACCESSIBLE>"
                            city = "<INACCESSIBLE>"
                            state = "<INACCESSIBLE>"
                            zc = "<INACCESSIBLE>"
                    if store == "3003":
                        add = "832 North State of Franklin Road"
                        city = "Johnson City"
                        state = "TN"
                        zc = "<INACCESSIBLE>"
                    if store == "3004":
                        add = "3016 North John B Dennis Highway"
                        city = "Kingsport"
                        state = "TN"
                        zc = "<INACCESSIBLE>"
                    if store == "3319":
                        add = "5010 S Highway 69/5423 S Hwy 69"
                        city = "McAlester"
                        state = "OK"
                        zc = "74501"
                    state = state.replace(" USA", "").replace(" US", "")
                    add2 = item.split(',"address":"')[1].split('"')[0]
                    add2 = add2.replace(", USA", "").replace(", ", ",")
                    if add2.count(",") == 2:
                        address = add2.split(",")[0]
                        city = add2.split(",")[1]
                        state = add2.split(",")[2]
                        zc = "<INACCESSIBLE>"
                    if "881 Windham Rd. S." in rawadd:
                        address = "881 Windham Rd. S."
                        city = "Windham"
                        state = "CT"
                        zc = "06266-1132"
                    if "1101 3rd Ave. S." in rawadd:
                        add = "1101 3rd Ave. S."
                        city = "Myrtle Beach"
                        state = "SC"
                        zc = "29577"
                    if "4530 Tynecastle Highway" in rawadd:
                        add = "4530 Tynecastle Highway"
                        city = "Banner Elk"
                        state = "NC"
                        zc = "28604"
                    yield [
                        website,
                        loc,
                        name,
                        address,
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
