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
    locator_domain = "https://woofgangbakery.com/"
    api_url = "https://storerocket.global.ssl.fastly.net/api/user/7OdJEZD8WE/locations"
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
    js = r.json()["results"]["locations"]

    for j in js:
        line = j.get("address").split(",")
        if j.get("address_line_1"):
            street_address = (
                f'{j.get("address_line_1")} {j.get("address_line_2") or ""}'.strip()
                or "<MISSING>"
            )
            city = j.get("city") or "<MISSING>"
            state = j.get("state") or "<MISSING>"
            postal = j.get("postcode") or "<MISSING>"
            country_code = j.get("country") or "<MISSING>"
        else:
            a = usaddress.tag(", ".join(line), tag_mapping=tag)[0]
            street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
            if street_address == "None":
                street_address = "<MISSING>"
            city = a.get("city") or "<INACCESSIBLE>"
            state = a.get("state") or "<INACCESSIBLE>"
            postal = a.get("postal") or "<INACCESSIBLE>"
            if city.find(",") != -1:
                state = city.split(",")[-1].strip()
                city = city.split(",")[0].strip()

        if len(postal) == 4:
            postal = f"0{postal}"

        store_number = j.get("id") or "<MISSING>"
        page_url = j.get("url") or "<MISSING>"
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        for d in days:
            time = j.get(d)
            if not time:
                break
            _tmp.append(f"{d}: {time}")

        hours_of_operation = ";".join(_tmp) or "Coming Soon"

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
