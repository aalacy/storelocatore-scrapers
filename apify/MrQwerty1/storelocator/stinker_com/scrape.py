import csv
import usaddress

from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sgzip.static import static_coordinate_list, SearchableCountries


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
    city = a.get("city") or "<INACCESSIBLE>"
    if city == "USA":
        city = "<INACCESSIBLE>"
    state = a.get("state") or "<INACCESSIBLE>"
    postal = a.get("postal") or "<INACCESSIBLE>"

    return street_address, city, state, postal


def get_token():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }
    r = session.get("https://www.stinker.com/store-search/", headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[@id='locator-js-extra']/text()"))
    token = text.split('"lkp":"')[1].split('"')[0].strip()

    return token


def get_data(coord, token):
    out = []
    lat, lng = coord
    locator_domain = "https://www.stinker.com/"
    api_url = f"https://www.stinker.com/system/wp-admin/admin-ajax.php?action=lookupLocations&lkp={token}&lat={lat}&lng={lng}"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["locations"]

    for j in js:
        loc = j.get("latLng")
        latitude = loc.get("latitude") or "<MISSING>"
        longitude = loc.get("longitude") or "<MISSING>"
        j = j.get("popupInfo")

        line = j.get("location")
        street_address, city, state, postal = get_address(line)
        country_code = "US"
        page_url = j.get("permalink") or "<MISSING>"
        location_name = j.get("title").replace("&#038;", "&")
        store_number = location_name.split()[0].replace("#", "")
        if not store_number.isdigit():
            store_number = "<MISSING>"
        phone = j["otherInfo"]["phone"] or "<MISSING>"

        location_type = "<MISSING>"
        hours = j.get("content")
        try:
            hours_of_operation = (
                hours.split("Hours:")[1]
                .replace("pm ", "pm; ")
                .split("</p>\n")[0]
                .strip()
            )
            if "<" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("<")[0].strip()
        except IndexError:
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


def fetch_data():
    out = []
    s = set()
    token = get_token()
    coords = static_coordinate_list(radius=25, country_code=SearchableCountries.USA)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(get_data, coord, token): coord for coord in coords
        }
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                check = tuple(row[2:6])
                if check not in s:
                    s.add(check)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
