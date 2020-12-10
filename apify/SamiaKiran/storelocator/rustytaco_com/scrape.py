import csv
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("rustytaco_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    final_data = []
    url = "https://rustytaco.com/locations-search/"
    r = session.get(url, headers=headers, verify=False)
    loclist = r.text.split("window.gmaps.items =")[1].split(
        "window.gmaps.order_url = ", 1
    )[0]
    loclist = loclist.replace(";", "").strip()
    loclist = json.loads(loclist)
    for loc in loclist:
        store = loc["id"]
        title = loc["name"]
        lat = loc["lat"]
        longt = loc["lng"]
        street = loc["custom_fields"]["address"]["street"]
        city = loc["custom_fields"]["address"]["city"]
        state = loc["custom_fields"]["address"]["state"]
        pcode = loc["custom_fields"]["address"]["zip"]
        phone = loc["custom_fields"]["phone"]
        if not phone:
            phone = "<MISSING>"
        hour_list = loc["custom_fields"]["hours"]
        hours = " "
        for hour in hour_list:
            open_time = hour["open_time"]
            close_time = hour["close_time"]
            day = hour["day"]
            hours = hours + day + " " + open_time + " " + close_time + " "
        final_data.append(
            [
                "https://rustytaco.com/",
                "https://rustytaco.com/locations-search/",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                store,
                phone,
                "<MISSING>",
                lat,
                longt,
                hours,
            ]
        )
    return final_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
