import csv
import json

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
    locator_domain = "https://www.supermex.com/"
    page_url = "https://www.supermex.com/locations"
    api_url = "https://websiteoutputapi.mopro.com/WebsiteOutput.svc/api/get"

    headers = {"Content-Type": "application/json"}

    data = {
        "method": "GetLocationLocatorByBounds",
        "parameters": "ProjectID=0a417951-89f2-4080-89f6-b747dd2a5360&SitePageModuleID=925008e1-e649-48cc-9019-43f500c2dc02&Bound1=48.9680,-46.1046&Bound2=21.5992,-148.9366&userLatlng=36.4770,-97.5206",
        "typefields": [{"DataType": "LocationLocatorRow", "Columns": "*"}],
    }

    session = SgRequests()
    r = session.post(api_url, headers=headers, data=json.dumps(data))
    js = r.json()[1]["rows"]

    for j in js:
        street_address = j.get("Address")
        csz = j.get("City")
        city = csz.split(",")[0].strip()
        csz = csz.split(",")[1].strip()
        state = csz.split()[0]
        postal = csz.split()[1]
        country_code = "US"
        store_number = j.get("index")
        location_name = j.get("Name")
        phone = j.get("Telephone")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
