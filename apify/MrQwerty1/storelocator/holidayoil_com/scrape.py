import csv

import usaddress
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
    locator_domain = "https://www.holidayoil.com/"
    api_url = "https://apps.elfsight.com/p/boot/?w=346ee1c6-13a6-4bf2-a2de-2235aa1117c3"

    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "BuildingName": "address2",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }

    session = SgRequests()
    r = session.get(api_url)
    jss = r.json()["data"]["widgets"].values()

    for js in jss:
        js = js["data"]["settings"]["markers"]
        for j in js:
            line = j.get("position")
            a = usaddress.tag(line, tag_mapping=tag)[0]
            street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
            if street_address == "None":
                street_address = "<MISSING>"
            city = a.get("city") or "<MISSING>"
            state = a.get("state") or "<MISSING>"
            postal = a.get("postal") or "<MISSING>"
            country_code = "US"
            page_url = "<MISSING>"
            location_name = j.get("infoTitle")
            if location_name.find("(") != -1:
                location_name = location_name.split("(")[0].strip()
            store_number = location_name.replace("#", "")
            phone = j.get("infoPhone") or "<MISSING>"
            try:
                latitude, longitude = j.get("coordinates").split(",")
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
            location_type = "<MISSING>"
            hours_of_operation = j.get("infoWorkingHours") or "<MISSING>"

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
