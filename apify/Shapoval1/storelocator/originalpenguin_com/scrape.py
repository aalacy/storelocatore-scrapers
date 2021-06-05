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

    locator_domain = "https://www.originalpenguin.com"
    api_url = "https://api.zenlocator.com/v1/apps/app_7tx9r8kr/locations/search?northeast=67.193746%2C31.935493&southwest=-26.135222%2C-180"

    session = SgRequests()
    r = session.get(api_url)

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

    js = r.json()
    for j in js["locations"]:
        line = "".join(j.get("visibleAddress")).replace("\n", "").strip()

        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = (
            f"{a.get('address1')} {a.get('address2')} {a.get('recipient')}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )
        city = a.get("city") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        try:
            phone = j.get("contacts").get("con_c4g3q3jz").get("text")
        except AttributeError:
            phone = "<MISSING>"

        country_code = "US"
        store_number = "<MISSING>"
        location_name = j.get("name")
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"
        tmp = ["fri", "mon", "sat", "sun", "thu", "tue", "wed"]
        _tmp = []
        for i in tmp:
            days = i
            time = j.get("hours").get("hoursOfOperation").get(i)
            line = f"{days} {time}"
            _tmp.append(line)
        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        page_url = "https://www.originalpenguin.com/pages/find-a-store"
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
