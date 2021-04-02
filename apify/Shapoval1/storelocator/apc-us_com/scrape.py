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
    }
    locator_domain = "https://www.apc-us.com"
    page_url = "https://www.apc-us.com/apps/store-locator#"
    api_url = "https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=apc-us.myshopify.com&latitude=40.76801299999998&longitude=-111.904099&max_distance=0&limit=100&calc_distance=0"
    session = SgRequests()
    r = session.post(api_url)
    js = r.json()

    for j in js["stores"]:
        ad = (
            f"{j.get('address')} {j.get('address2')}".replace("\n", "")
            .replace(" | ", " ")
            .strip()
        )
        if ad.find("Havre 68") != -1:
            continue
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')} {a.get('SecondStreetName')} {a.get('SecondStreetNamePostType')}".replace(
            "None", ""
        ).strip()
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("ZipCode") or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "".join(j.get("name"))
        if location_name == "A.P.C.":
            location_name = location_name + " " + " ".join(street_address.split()[1:])
        phone = "".join(j.get("phone"))
        if phone.find("<") != -1:
            phone = "".join(j.get("phone")).split(">")[1].split("<")[0]
        phone = phone or "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"
        hours_of_operation = "".join(j.get("hours")).replace("\r\n", " ").strip()
        if hours_of_operation.find("Sat") == -1:
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
