import csv
import usaddress
from lxml import html
from sgrequests import SgRequests
from concurrent import futures


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
    r = session.get(
        "https://www.nightlitepediatrics.com/locations-pediatrics-urgent-care-in-florida"
    )
    tree = html.fromstring(r.text)
    return tree.xpath("//a[./span[contains(text(), 'More')]]/@href")


def get_data(url):
    locator_domain = "https://www.nightlitepediatrics.com"
    page_url = f"{locator_domain}{url}"
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
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    ad = " ".join(tree.xpath('//span[@style="text-decoration: underline;"]/text()'))
    if ad.find("CALL") == -1:
        a = usaddress.tag(ad, tag_mapping=tag)[0]
    else:
        a = "<MISSING>"
    try:
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
    except AttributeError:
        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    location_name = "".join(tree.xpath("//h1/text()"))
    if location_name.find("Directions to") != -1:
        location_name = location_name.split("Directions to")[1].split(",")[0].strip()
    text = "".join(tree.xpath("//h3/a/@href"))
    try:
        if text.find("ll=") != -1:
            latitude = text.split("ll=")[1].split(",")[0]
            longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        " ".join(
            tree.xpath(
                "//strong[contains(text(), 'Hours')]/following-sibling::text()[1] | //h3[contains(text(), 'Hours')]/text()[1]"
            )
        )
        .replace("\n", "")
        .strip()
    )
    if hours_of_operation.find("Open Hours:") != -1:
        hours_of_operation = (
            hours_of_operation.split("Open Hours:")[1].split("Open")[0].strip()
        )
    if hours_of_operation.find("Open") != -1:
        hours_of_operation = hours_of_operation.split("Open")[1].strip()
    phone_urls = locator_domain + "".join(
        tree.xpath("//a[contains(text(), 'Call')]/@href")
    )
    session = SgRequests()
    r = session.get(phone_urls)
    subtree = html.fromstring(r.text)
    phone = (
        "".join(subtree.xpath('//a[contains(text(), "New Patients")]/text()'))
        .split("New Patients:")[1]
        .strip()
    )

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
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
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
