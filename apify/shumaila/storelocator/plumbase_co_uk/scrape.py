import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("plumbase_com")


session = SgRequests()


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
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    data = []
    base_url = "https://www.plumbase.co.uk/storefinder/stores"
    r = session.get(base_url, headers=headers)
    s = json.loads(r.text)
    s = s["all"]
    for loc in s:

        title = loc["LocationName"]
        phone = loc["Phone"]
        if loc["Address4"]:
            street = loc["Address1"] + ", " + loc["Address2"] + ", " + loc["Address3"]
            city = loc["Address4"]
        else:
            street = loc["Address1"] + ", " + loc["Address2"]
            city = loc["Address3"]
        state = "<MISSING>"
        zip = loc["postcode"]
        lat = loc["Lat"]
        lng = loc["Lng"]
        if loc["Brand"]:
            store_type = loc["Brand"]
        else:
            store_type = "<MISSING>"
        storenum = loc["BranchID"]
        if loc["SmallTimes"]:
            weekday = (
                loc["SmallTimes"][0]["DayOfWeek"]
                + ": "
                + loc["SmallTimes"][0]["OpeningAt"]
                + " - "
                + loc["SmallTimes"][0]["ClosingAt"]
            )
            sat = (
                loc["SmallTimes"][1]["DayOfWeek"]
                + ": "
                + loc["SmallTimes"][1]["OpeningAt"]
                + " - "
                + loc["SmallTimes"][1]["ClosingAt"]
            )
            sun = (
                loc["SmallTimes"][2]["DayOfWeek"]
                + ": "
                + loc["SmallTimes"][2]["OpeningAt"]
                + " - "
                + loc["SmallTimes"][2]["ClosingAt"]
            )
            if sun.find("Closed") != -1:
                sun = sun.replace("-", "").rstrip()
            hours_of_operation = weekday + " " + sat + " " + sun
        else:
            hours_of_operation = "<MISSING>"
        data.append(
            [
                "https://www.plumbase.co.uk",
                "https://www.plumbase.co.uk/storefinder/stores",
                title,
                street,
                city,
                state,
                zip,
                "UK",
                storenum,
                phone,
                store_type,
                lat,
                lng,
                hours_of_operation,
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
