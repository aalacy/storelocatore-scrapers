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
    session = SgRequests()
    r = session.get("https://www.seafoodcity.com/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//ul[@class='children']//a[contains(@href, '/store-locations/')]/@href"
    )


def get_data(page_url):
    rows = []
    locator_domain = "https://www.seafoodcity.com/"
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
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[@class='stores-container']")
    for d in divs:
        iscoming = False
        location_name = "".join(d.xpath("./h3/text()")).strip()
        if location_name.lower().find("soon") != -1:
            iscoming = True
        line = "".join(d.xpath("./p[1]/text()")).strip()
        if page_url.find("canada") == -1:
            a = usaddress.tag(line, tag_mapping=tag)[0]
            street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
            if street_address == "None":
                street_address = "<MISSING>"
            city = a.get("city").strip() or "<MISSING>"
            if city.endswith(","):
                city = city[:-1]
            state = a.get("state") or "<MISSING>"
            postal = a.get("postal") or "<MISSING>"
            country_code = "US"
        else:
            line = line.replace(", Canada", "").replace("Alberta", "AB").strip()
            if location_name.find("(") != -1:
                location_name = location_name.split("(")[0].strip()

            city = location_name
            if line.find(city) != -1:
                line = line.replace(",", "")
                street_address = line.split(city)[0].strip()
                line = line.split(city)[1].strip()
                state = line.split()[0]
                postal = " ".join(line.split()[1:])
            else:
                street_address = line.split(".")[0].strip()
                line = line.split(".")[1].strip()
                city = line.split()[0]
                state = line.split()[1]
                postal = " ".join(line.split()[2:])
            country_code = "CA"

        store_number = "<MISSING>"
        location_type = "<MISSING>"
        try:
            phone = (
                d.xpath(".//p[contains(text(), 'Tel')]/text()")[0]
                .replace("Tel.", "")
                .strip()
                or "<MISSING>"
            )
        except IndexError:
            phone = "<MISSING>"

        text = "".join(d.xpath(".//a[contains(@href, 'maps')]/@href"))
        try:
            if text.find("ll=") != -1:
                latitude, longitude = text.split("ll=")[1].split("&")[0].split(",")
            elif text.find("@") != -1:
                latitude, longitude = text.split("@")[1].split(",")[:2]
            else:
                latitude, longitude = "<MISSING>", "<MISSING>"
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"

        _tmp = []
        hours = d.xpath(".//p[contains(text(), 'Store Hours:')]/text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        for h in hours:
            if h.lower().find("store") != -1:
                continue
            _tmp.append(h)

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        if iscoming:
            hours_of_operation = "Coming Soon"

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
