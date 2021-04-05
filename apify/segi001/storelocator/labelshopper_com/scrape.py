import csv
from sgrequests import SgRequests
import bs4
import re
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
    locator_domain = "https://www.labelshopper.com/"
    all_stores = "https://www.labelshopper.com/wp-json/wpgmza/v1/marker-listing/"
    missingString = "<MISSING>"
    pageURL = "https://www.labelshopper.com/find-stores/"

    s = SgRequests()

    nonceSource = s.get("https://www.labelshopper.com/find-stores/").text

    nonceScript = bs4.BeautifulSoup(nonceSource, features="lxml").find(
        "script", {"id": "wpgmza-js-extra"}
    )

    nonceVariable = re.search(
        r"WPGMZA_localized_data = (.*?);", str(nonceScript)
    ).group(1)

    nonceCookie = json.loads(nonceVariable)

    header = {
        "x-wp-nonce": nonceCookie["restnonce"],
        "x-wpgmza-action-nonce": nonceCookie["restnoncetable"]["/marker-listing/"],
    }

    formData = {
        "phpClass": r"WPGMZA\MarkerListing\BasicTable",
        "start": "0",
        "length": "100",
        "map_id": "1",
    }

    storeSource = json.loads(s.post(all_stores, data=formData, headers=header).text)[
        "meta"
    ]

    result = []

    i = 0

    def isZIP(string):
        return any(char.isdigit() for char in string)

    def getStateAndAddress(string):
        state = ""
        address = ""
        if "Unit" in string.split(",")[-2] or "Suite" in string.split(",")[-2]:
            state = string.split(",")[-2].split(" ")[-1]
            address = string.replace(",", "")[:-1]
        else:
            state = string.split(",")[-2].replace(" ", "", 1)
            address = string.replace(",", "")[:-1]
        return [state, address]

    for store in storeSource:
        i += 1
        zipC = ""

        if isZIP(store["address"].split(" ")[-1]):
            zipC = store["address"].split(" ")[-1]
        else:
            zipC = missingString

        addressJSON = {
            "zip": zipC,
            "state": store["address"].split(" ")[-2].replace(",", ""),
            "city": getStateAndAddress(
                store["address"].split(
                    store["address"].split(" ")[-2].replace(",", "")
                )[0]
            )[0],
            "address": getStateAndAddress(
                store["address"].split(
                    store["address"].split(" ")[-2].replace(",", "")
                )[0]
            )[1],
        }

        phone = (
            bs4.BeautifulSoup(store["description"], features="lxml")
            .findAll("a")[1]
            .text
        )

        time = (
            str(bs4.BeautifulSoup(store["description"], features="lxml").find("ul"))
            .replace("<ul>", "")
            .replace("</ul>", "")
            .replace("<li>", "")
            .replace("</li>", ", ")[:-2]
        )
        result.append(
            [
                locator_domain,
                pageURL,
                store["title"],
                addressJSON["address"],
                addressJSON["city"],
                addressJSON["state"],
                addressJSON["zip"],
                missingString,
                i,
                phone,
                missingString,
                store["lat"],
                store["lng"],
                time,
            ]
        )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
