import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "authorization": "Bearer eB85lVGzjUf0929F3Avp2mjm8pg01r",
}

logger = SgLogSetup().get_logger("choptsalad_com")


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
    url = "https://ordering-api.choptsalad.com/api/v1/locations"
    r = session.get(url, headers=headers)
    website = "choptsalad.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    store = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"display_name":"' in line:
            items = line.split('"display_name":"')
            for item in items:
                hours = ""
                if '{"success":' not in item:
                    name = item.split('"')[0]
                    add = item.split('"address1":"')[1].split('"')[0]
                    try:
                        add = add + " " + item.split('"address2":"')[1].split('"')[0]
                    except:
                        pass
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"zip":"')[1].split('"')[0]
                    phone = item.split('"phone":"')[1].split('"')[0]
                    lat = item.split('"lat":')[1].split(",")[0]
                    lng = item.split('"lng":')[1].split(",")[0]
                    try:
                        h1 = (
                            "Sun: "
                            + item.split(
                                '"pickup","day_of_week":0,"day_name":"Sunday","start_time":"'
                            )[1].split('"')[0]
                            + "-"
                            + item.split(
                                '"pickup","day_of_week":0,"day_name":"Sunday"'
                            )[1]
                            .split('"end_time":"')[1]
                            .split('"')[0]
                        )
                    except:
                        h1 = "Sun: Closed"
                    try:
                        h2 = (
                            "Mon: "
                            + item.split(
                                '"pickup","day_of_week":1,"day_name":"Monday","start_time":"'
                            )[1].split('"')[0]
                            + "-"
                            + item.split(
                                '"pickup","day_of_week":1,"day_name":"Monday"'
                            )[1]
                            .split('"end_time":"')[1]
                            .split('"')[0]
                        )
                    except:
                        h2 = "Mon: Closed"
                    try:
                        h3 = (
                            "Tue: "
                            + item.split(
                                '"pickup","day_of_week":2,"day_name":"Tuesday","start_time":"'
                            )[1].split('"')[0]
                            + "-"
                            + item.split(
                                '"pickup","day_of_week":2,"day_name":"Tuesday"'
                            )[1]
                            .split('"end_time":"')[1]
                            .split('"')[0]
                        )
                    except:
                        h3 = "Tue: Closed"
                    try:
                        h4 = (
                            "Wed: "
                            + item.split(
                                '"pickup","day_of_week":3,"day_name":"Wednesday","start_time":"'
                            )[1].split('"')[0]
                            + "-"
                            + item.split(
                                '"pickup","day_of_week":3,"day_name":"Wednesday"'
                            )[1]
                            .split('"end_time":"')[1]
                            .split('"')[0]
                        )
                    except:
                        h4 = "Wed: Closed"
                    try:
                        h5 = (
                            "Thu: "
                            + item.split(
                                '"pickup","day_of_week":4,"day_name":"Thursday","start_time":"'
                            )[1].split('"')[0]
                            + "-"
                            + item.split(
                                '"pickup","day_of_week":4,"day_name":"Thursday"'
                            )[1]
                            .split('"end_time":"')[1]
                            .split('"')[0]
                        )
                    except:
                        h5 = "Thu: Closed"
                    try:
                        h6 = (
                            "Fri: "
                            + item.split(
                                '"pickup","day_of_week":5,"day_name":"Friday","start_time":"'
                            )[1].split('"')[0]
                            + "-"
                            + item.split(
                                '"pickup","day_of_week":5,"day_name":"Friday"'
                            )[1]
                            .split('"end_time":"')[1]
                            .split('"')[0]
                        )
                    except:
                        h6 = "Fri: Closed"
                    try:
                        h7 = (
                            "Sat: "
                            + item.split(
                                '"pickup","day_of_week":6,"day_name":"Saturday","start_time":"'
                            )[1].split('"')[0]
                            + "-"
                            + item.split(
                                '"pickup","day_of_week":6,"day_name":"Saturday"'
                            )[1]
                            .split('"end_time":"')[1]
                            .split('"')[0]
                        )
                    except:
                        h7 = "Sat: Closed"
                    hours = (
                        h1
                        + "; "
                        + h2
                        + "; "
                        + h3
                        + "; "
                        + h4
                        + "; "
                        + h5
                        + "; "
                        + h6
                        + "; "
                        + h7
                    )
                    if hours == "":
                        hours = "<MISSING>"
                    name = name.replace("\\", "")
                    add = add.replace("\\", "")
                    if "0" not in hours:
                        hours = "Sun-Sat: Closed"
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
