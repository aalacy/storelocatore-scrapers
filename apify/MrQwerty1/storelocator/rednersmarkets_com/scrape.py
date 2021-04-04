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
    locator_domain = "https://www.rednersmarkets.com/"
    api_url = "https://www.rednersmarkets.com/wp-admin/admin-ajax.php"
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

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "X-Requested-With": "XMLHttpRequest",
    }

    data = [
        ("action", "ldm_map_locations"),
        ("tilesNeeded[]", "4-11"),
        ("tilesNeeded[]", "4-12"),
        ("tilesNeeded[]", "4-13"),
        ("tilesNeeded[]", "5-11"),
        ("tilesNeeded[]", "5-12"),
        ("tilesNeeded[]", "5-13"),
        ("tilesNeeded[]", "6-11"),
        ("tilesNeeded[]", "7-11"),
        ("tilesNeeded[]", "8-11"),
        ("tilesNeeded[]", "9-11"),
        ("tilesNeeded[]", "9-12"),
        ("tilesNeeded[]", "9-13"),
    ]

    session = SgRequests()
    r = session.post(api_url, headers=headers, data=data)
    js = r.json().values()

    for jj in js:
        for j in jj:
            p = j.get("ldm_map_properties")
            line = p.get("address")
            a = usaddress.tag(line, tag_mapping=tag)[0]
            street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
            if street_address == "None":
                street_address = "<MISSING>"
            city = a.get("city") or "<MISSING>"
            state = a.get("state") or "<MISSING>"
            postal = a.get("postal") or "<MISSING>"
            country_code = "US"

            store_number = "<MISSING>"
            page_url = p.get("permalink") or "<MISSING>"
            location_name = j.get("post_title") or "<MISSING>"
            phone = p.get("phone") or "<MISSING>"
            latitude = j.get("ldm_map_lat") or "<MISSING>"
            longitude = j.get("ldm_map_lng") or "<MISSING>"
            location_type = ",".join(p.get("type")) or "<MISSING>"
            hours_of_operation = p.get("hours") or "<MISSING>"

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
