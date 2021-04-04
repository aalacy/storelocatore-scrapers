import csv
from sgrequests import SgRequests
import json


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
    locator_domain = "https://www.rentawheel.com/"
    api = "https://api.ridestyler.net/Location/List"
    missingString = "<MISSING>"
    h = {
        "Content-Type": "application/json",
        "Authorization": "ApiKey 3764acce-4d8c-42cb-bca0-bae367430492",
    }

    s = SgRequests()
    api = s.post(api, headers=h).text

    apiJSON = json.loads(api)["Locations"]

    result = []

    for el in apiJSON:
        timeArray = []
        lochours = el["LocationHours"]
        for e in el["LocationHours"]:
            o = lochours[e]["Open"]
            c = lochours[e]["Close"]
            if lochours[e]["Operational"] == "true":
                timeArray.append("{} - {}".format(o, c))
            else:
                pass
        hours = ", ".join(timeArray)
        if hours == "":
            hours = missingString
        result.append(
            [
                locator_domain,
                missingString,
                el["LocationName"],
                el["LocationAddress1"],
                el["LocationCity"],
                el["LocationState"],
                el["LocationPostalCode"],
                el["LocationCountry"],
                el["LocationID"],
                el["LocationSalesPhone"],
                missingString,
                el["LocationLatitude"],
                el["LocationLongitude"],
                hours,
            ]
        )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
