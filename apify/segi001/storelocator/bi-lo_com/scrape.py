import csv
from sgrequests import SgRequests
import bs4
import json
import re


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

    locator_domain = "https://www.bi-lo.com/"
    backendPOST = (
        "https://www.bi-lo.com/Locator?search=29607&MilesSelectedValue=1000000"
    )

    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }
    missingString = "<MISSING>"
    s = SgRequests()
    tokenSource = s.get(backendPOST, headers=headers)
    soup = bs4.BeautifulSoup(tokenSource.text, features="lxml")
    verificationToken = soup.find("input", {"name": "__RequestVerificationToken"})[
        "value"
    ]
    payload = {
        "__RequestVerificationToken": verificationToken,
        "fhController": "ContentComponentsController",
        "fhAction": "StoreLocatorResults",
        "sitename": "bilo",
        "bannerName": "BI-LO+%23+",
        "currentzipcode": "29607",
        "CurrentState": "StrTab",
        "StoreZipCode": "29607",
        "MilesSelectedValue": "20000",
        "strCommand": "Search",
        "ATM": "false",
        "Floral": "false",
        "Lottery": "false",
        "RedBox": "false",
        "CoinCounter": "false",
        "FreshMeat": "false",
        "MTMO": "false",
        "SeaFood": "false",
        "DeliBakery": "false",
        "GlutenFree": "false",
        "Pharmacy": "false",
        "Sushi": "false",
        "ATM": "false",
        "Floral": "false",
        "Lottery": "false",
        "RedBox": "false",
        "CoinCounter": "false",
        "FreshMeat": "false",
        "MTMO": "false",
        "SeaFood": "false",
        "DeliBakery": "false",
        "GlutenFree": "false",
        "Pharmacy": "false",
        "Sushi": "false",
    }
    html = s.post(backendPOST, data=payload).text
    locations = json.loads(
        re.compile(r"var locations  = (.*?);", re.DOTALL).findall(html)[0].strip()
    )
    result = []
    for el in locations:
        page_url = el[10]
        name = el[3]
        dividerCounter = el[0].count(",")
        addressInfo = missingString
        if dividerCounter == 3:
            addressInfo = el[0].replace(",", "", 1).strip().split(",")
        else:
            addressInfo = el[0].strip().split(",")
        addressJSON = {
            "address": addressInfo[0],
            "city": addressInfo[1].strip(),
            "country": addressInfo[2].split(" ")[1],
            "zip": addressInfo[2].split(" ")[2],
            "lat": el[1],
            "lng": el[2],
        }
        country_code = missingString
        store_number = el[12]
        phone = el[7]
        location_type = missingString
        hours = (
            el[4]
            .replace("<span class=blackfontIndi></span>", "")
            .replace("to", "-")
            .strip()
        )
        hours_of_operation = "Mon-Fri: {}, Sat: {}, Sun: {}".format(hours, hours, hours)
        result.append(
            [
                locator_domain,
                page_url,
                name,
                addressJSON["address"],
                addressJSON["city"],
                addressJSON["country"],
                addressJSON["zip"],
                country_code,
                store_number,
                phone,
                location_type,
                addressJSON["lat"],
                addressJSON["lng"],
                hours_of_operation,
            ]
        )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
