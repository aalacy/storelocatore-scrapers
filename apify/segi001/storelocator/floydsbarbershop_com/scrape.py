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
    s = SgRequests()

    data = {
        "StartIndex": 0,
        "EndIndex": 10000,
        "Longitude": 0,
        "Latitude": 0,
        "F": "GetAllLocations",
    }

    locator_domain = "https://www.floydsbarbershop.com"
    api_url = "https://www.floydsbarbershop.com/modules/staff/ajax.aspx"
    missingString = "<MISSING>"

    storeData = json.loads(s.post(api_url, data=data).text)

    result = []

    def ruleset(string):
        return string.replace("<strong>", "").replace("</strong>", "")

    for el in storeData:
        result.append(
            [
                locator_domain,
                locator_domain + el["CustomUrl"],
                el["Name"],
                "{} {}".format(el["Address1"], el["Address2"]),
                el["City"],
                el["State"],
                el["Zip"],
                missingString,
                el["SCId"],
                el["Phone"],
                missingString,
                el["Latitude"],
                el["Longitude"],
                "{} : {}-{},{} : {}-{},{} : {}-{}".format(
                    ruleset(el["OpenHours"][0]["DayName"]),
                    ruleset(el["OpenHours"][0]["OpenHrs"]),
                    ruleset(el["OpenHours"][0]["CloseHrs"]),
                    ruleset(el["OpenHours"][1]["DayName"]),
                    ruleset(el["OpenHours"][1]["OpenHrs"]),
                    ruleset(el["OpenHours"][1]["CloseHrs"]),
                    ruleset(el["OpenHours"][2]["DayName"]),
                    ruleset(el["OpenHours"][2]["OpenHrs"]),
                    ruleset(el["OpenHours"][2]["CloseHrs"]),
                ),
            ]
        )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
