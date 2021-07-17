import csv
import json
from lxml import html
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
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
    out = []

    locator_domain = "https://www.totalwireless.com"
    api_url = "https://www.mapquestapi.com/search/v2/radius?callback=jQuery11120795672774391978_1626436007537&key=Gmjtd%7Cluub2qu2nu%2C85%3Do5-lzt2g&ambiguities=ignore&maxMatches=30&units=m&hostedData=mqap.37706_all_brands_CashForService%7C%22BRANDTW%22%3D%3F+AND+%22ISEXCLUSIVE%22%3D%3F%7Ctrue%2Ctrue%7CDAPID%2CNAME%2CADDRESS%2CCITY%2CSTATE%2CZIPCODE%2CPHONE%2Cmqap_geography%2CSTORETYPE%2CISEXCLUSIVE%2CISSPECIALTY%2CLINK%2CSERVICEDELIVERY%2CSERVICEAPPOINTMENT%2CSERVICEPAYMENTTYPES%2CSERVICEDELIVERYTYPES%2CBRANDTW&radius=15&origin=Miami+FL&_=1626436007543"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    jsblock = r.text.split('"searchResults":')[1].split(',"info"')[0].strip()
    js = json.loads(jsblock)
    for j in js:
        a = j.get("fields")
        location_name = j.get("name")
        page_url = a.get("LINK") or "https://www.totalwireless.com/findastore"
        location_type = "Exclusive location"
        street_address = a.get("ADDRESS")
        state = a.get("STATE")
        postal = a.get("ZIPCODE")
        country_code = "US"
        city = a.get("CITY")
        store_number = "<MISSING>"
        latitude = a.get("mqap_geography").get("latLng").get("lat")
        longitude = a.get("mqap_geography").get("latLng").get("lng")
        phone = a.get("PHONE")

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//table//tr[contains(@class, "c-location-hours-details-row js-day-of-week-row highlight-text")]/td//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = hours_of_operation.replace("  -  ", " - ")

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
