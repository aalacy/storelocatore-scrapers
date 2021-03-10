import csv
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


def get_urls():
    urls = []
    geo = dict()
    s = set()
    session = SgRequests()
    data = {
        "categoryID": 0,
        "currentUserItems": False,
        "publicGUID": "",
        "tagID": 0,
        "keywords": "",
        "customFieldFilters": [],
    }

    r = session.post(
        "https://www.alafarm.com/services/businessesservice.asmx/GetBusinessMapData",
        json=data,
    )
    js = r.json()["d"]["Markers"]
    for j in js:
        _id = j.get("HoverURL", "").split("=")[-1]
        if _id in s:
            continue

        s.add(_id)
        urls.append(f"https://www.alafarm.com/business_detail.aspx?id={_id}")
        lat = j.get("Lat") or "<MISSING>"
        lng = j.get("Lng") or "<MISSING>"
        geo[str(_id)] = {"lat": lat, "lng": lng}

    return urls, geo


def get_data(url, geo):
    locator_domain = "https://www.alafarm.com/"
    session = SgRequests()
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

    r = session.get(url)
    page_url = r.url
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1[@itemprop='name']/span/text()")).strip()
    line = "".join(tree.xpath("//a[contains(@id, 'location_0')]/text()")).strip()
    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
    if street_address == "None":
        street_address = "<MISSING>"
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    postal = a.get("postal") or "<MISSING>"
    country_code = "US"
    store_number = url.split("=")[-1]
    phone = tree.xpath("//div[./strong[contains(text(), 'Contact')]]/text()")
    phone = list(filter(None, [p.strip() for p in phone]))
    if phone:
        phone = phone[-1]
    else:
        try:
            phone = (
                tree.xpath("//span[contains(text(), ' - ')]/text()")[0]
                .replace("-", "")
                .strip()
            )
        except IndexError:
            phone = "<MISSING>"
    latitude = geo[store_number]["lat"]
    longitude = geo[store_number]["lng"]
    location_type = "<MISSING>"

    _tmp = []
    hours = tree.xpath("//div[./strong[contains(text(), 'Hours')]]/text()")
    hours = list(filter(None, [h.strip() for h in hours]))

    for h in hours:
        if h.find("am") != -1 or h.find("pm") != -1:
            _tmp.append(h)

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
    urls, geo = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, geo): url for url in urls}
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
