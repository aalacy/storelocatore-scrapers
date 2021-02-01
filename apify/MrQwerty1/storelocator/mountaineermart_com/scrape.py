import csv
import re
import usaddress

from concurrent import futures
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


def get_ids():
    ids = []
    coords = {}
    session = SgRequests()
    r = session.get(
        "http://www.mountaineermart.com/wp-json/wpgmza/v1/datatables/base64eJy1kjFrwzAQhf-LmzUkbbpoCx26NDTQQiB1KFfrYovKsjnJpmDy3ys5DnTrUm-3Hve+G+6N6Oru0VEI0Djsn3bHbVHsSL5Ynm2I1ldFsTUD+ZLNG306hkKIJBF6peDYV7GGXq+SaKj7sCZhNsgi1H3WifuenJNC2bq+8VmPMBRpInhqOEUylUnKejqho-Ss0Iph+W1cV6BHDOT6OSdc8Tf0mVzgy0Xd2OsF2XcLsu8XZG8WZD-8P-s0x6bGXNsz-dXYZIFCibzyN0jhbF1kSWXek1CTKjgmsx1YxBqee-6ST71yzHO4RX8AqQ8J6g"
    )
    js = r.json()["data"]
    for j in js:
        name = j[1]
        _id = "".join(re.findall(r"MM(\d+)", name))
        ids.append(_id)
        coords[_id] = j[3]

    return coords, ids


def get_data(store_number, coords):
    locator_domain = "http://www.mountaineermart.com/"
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

    if store_number != "15":
        page_url = f"http://www.mountaineermart.com/locations/mm{store_number}/"
    else:
        page_url = f"http://www.mountaineermart.com/locations/mart{store_number}/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    text = tree.xpath("//figcaption/text()")
    text = list(filter(None, [t.strip() for t in text]))
    line = text[-1].split("(")[0]
    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
    if street_address == "None":
        street_address = "<MISSING>"
    city = a.get("city") or "<INACCESSIBLE>"
    state = a.get("state") or "<INACCESSIBLE>"
    postal = a.get("postal") or "<INACCESSIBLE>"
    country_code = "US"
    location_name = f"Mountaineer Mart #{store_number} {city}"
    phone = "(" + text[-1].split("(")[-1]
    latitude, longitude = coords[store_number].split(",")
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

    return row


def fetch_data():
    out = []
    coords, ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, _id, coords): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
