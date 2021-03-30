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
    locator_domain = "https://www.heritagecooperative.com/"
    api_url = "https://www.heritagecooperative.com/atlasapi/RPLocationsApi/GetLocations?services=Agronomy%7CEnergy%7CFeed%7CGrain%7CStore"

    session = SgRequests()
    r = session.get(api_url)
    text = json.loads(r.text)
    js = eval(text.replace("null", "None").replace("false", "False"))

    for j in js:
        location_name = j.get("Name")
        if location_name.lower().find("country") == -1:
            continue
        street_address = j.get("StreetAddress") or "<MISSING>"
        city = j.get("City") or "<MISSING>"
        state = j.get("State") or "<MISSING>"
        postal = j.get("ZipCode") or "<MISSING>"
        country_code = j.get("Country") or "<MISSING>"
        if country_code == "United States":
            country_code = "US"

        store_number = j.get("LocationsID") or "<MISSING>"
        page_url = f'https://www.heritagecooperative.com{j.get("LocationURL")}'
        phone = j.get("Phone") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = j.get("Hours") or "<MISSING>"
        hours_of_operation = hours_of_operation.replace("\r\n", " ").replace(
            "pm", "pm;"
        )

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
