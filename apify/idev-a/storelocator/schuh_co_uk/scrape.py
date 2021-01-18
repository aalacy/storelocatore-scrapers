import csv
import json
from sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list

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


def parseTime(from_date, to_date):
    return (
        str(from_date)[:-2]
        + ":"
        + str(from_date)[2:]
        + "-"
        + str(to_date)[:-2]
        + ":"
        + str(to_date)[2:]
    )


def fetch_data():
    base_url = "https://www.schuh.co.uk"
    zip_codes = static_zipcode_list(radius=50, country_code=SearchableCountries.BRITAIN)
    data = []
    store_ids = []
    for zip_code in zip_codes:
        payload = {"culture": "en-gb", "searchString": zip_code}
        res = session.post(
            "https://schuhservice.schuh.co.uk/StoreFinderService/GetNearByBranchesBySearch",
            json=payload,
        )
        if "No Results" in res.text:
            continue
        store_list = json.loads(
            json.loads(res.text.replace("'", "\\/'").replace('\\"', "'"))["d"]
            .replace("'", '"')
            .replace('/"', "'")
        )
        for store in store_list:
            payload = {"branchName": store["BranchName"], "culture": "en-gb"}
            res1 = session.post(
                "https://schuhservice.schuh.co.uk/StoreFinderService/GetAdditionalBranchInfo",
                json=payload,
            )
            detail = json.loads(
                json.loads(res1.text.replace("'", "\\/'").replace('\\"', "'"))["d"]
                .replace("'", '"')
                .replace('/"', "'")
            )
            if detail["BranchRef"] in store_ids:
                continue
            store_ids.append(detail["BranchRef"])
            page_url = "https://www.schuh.co.uk/stores/" + store["BranchName"]
            location_name = detail["BranchName"]
            street_address = detail["BranchAddress1"]
            store_number = "<MISSING>"
            city = detail["BranchCity"]
            state = "<MISSING>"
            zip = detail["BranchPostcode"]
            hours_of_operation = ""
            hours_of_operation += (
                "Mon: "
                + (
                    "Closed"
                    if detail["MonOpen"] == 0
                    else parseTime(detail["MonOpen"], detail["MonClose"])
                )
                + " "
            )
            hours_of_operation += (
                "Tue: "
                + (
                    "Closed"
                    if detail["TueOpen"] == 0
                    else parseTime(detail["TueOpen"], detail["TueClose"])
                )
                + " "
            )
            hours_of_operation += (
                "Wed: "
                + (
                    "Closed"
                    if detail["WedOpen"] == 0
                    else parseTime(detail["WedOpen"], detail["WedClose"])
                )
                + " "
            )
            hours_of_operation += (
                "Thu: "
                + (
                    "Closed"
                    if detail["ThuOpen"] == 0
                    else parseTime(detail["ThuOpen"], detail["ThuClose"])
                )
                + " "
            )
            hours_of_operation += (
                "Fri: "
                + (
                    "Closed"
                    if detail["FriOpen"] == 0
                    else parseTime(detail["FriOpen"], detail["FriClose"])
                )
                + " "
            )
            hours_of_operation += (
                "Sat: "
                + (
                    "Closed"
                    if detail["SatOpen"] == 0
                    else parseTime(detail["SatOpen"], detail["SatClose"])
                )
                + " "
            )
            hours_of_operation += "Sun: " + (
                "Closed"
                if detail["SunOpen"] == 0
                else parseTime(detail["SunOpen"], detail["SunClose"])
            )
            country_code = "UK"
            phone = store["BranchPhone"].replace("\xa0", "")
            location_type = "<MISSING>"
            latitude = store["BranchLatitude"]
            longitude = store["BranchLongitude"]

            data.append(
                [
                    base_url,
                    page_url,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip,
                    country_code,
                    store_number,
                    '="' + phone + '"',
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                ]
            )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
