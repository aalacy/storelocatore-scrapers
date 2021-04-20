import csv
import usaddress

from concurrent import futures
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


def get_address(line):
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
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }

    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
    if street_address == "None":
        street_address = "<MISSING>"
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    postal = a.get("postal") or "<MISSING>"

    return street_address, city, state, postal


def get_urls():
    urls = []
    session = SgRequests()
    r = session.get(
        "https://www.edwardjones.com/api/financial-advisor/results?q=75022&distance=5000"
    )
    count = r.json()["resultCount"]

    for i in range(1, int(count / 15) + 2):
        urls.append(
            f"https://www.edwardjones.com/api/financial-advisor/results?q=75022&distance=5000&page={i}"
        )

    return urls


def get_data(url):
    rows = []
    locator_domain = "https://www.edwardjones.com"

    session = SgRequests()
    r = session.get(url)
    js = r.json()["results"]

    for j in js:
        location_name = j.get("faName")
        line = j.get("address") or "<MISSING>"
        try:
            street_address, city, state, postal = get_address(line)
        except usaddress.RepeatedLabelError:
            postal = line.split()[-1]
            state = line.split()[-2]
            line = line.replace(postal, "").replace(state, "").strip()
            if line.endswith(","):
                line = line[:-1]
            city = line.split(",")[-1]
            street_address = line.replace(city, "").strip()
            if street_address.endswith(","):
                street_address = street_address[:-1]
        country_code = "US"
        slug = j.get("faUrl")
        page_url = f"{locator_domain}{slug}"
        store_number = j.get("faEntityId") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lon") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<INACCESSIBLE>"

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
        rows.append(row)

    return rows


def fetch_data():
    out = []
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
