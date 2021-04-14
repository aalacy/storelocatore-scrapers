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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get("https://www.cityvet.com/my-location/", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath("//header/h2/a/@href")


def get_data(url):
    locator_domain = "https://www.cityvet.com"
    page_url = url
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
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
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    line = " ".join(
        tree.xpath(
            '//span[./i[@class="fas fa-map-marker-alt"]]/following-sibling::span/text()'
        )
    )
    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2')}".replace(
        "None", ""
    ).strip()
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")
    country_code = "US"
    store_number = "<MISSING>"
    location_name = "".join(tree.xpath("//h1/text()"))
    phone = (
        "".join(
            tree.xpath(
                '//span[./i[@class="fas fa-phone-alt"]]/following-sibling::span/text()'
            )
        )
        or "<MISSING>"
    )
    if phone.find("P") != -1:
        phone = phone.split("P")[1].split("|")[0].strip()
    text = "".join(
        tree.xpath('//li/a[./span[./i[@class="fas fa-map-marker-alt"]]]/@href')
    )
    try:
        if text.find("ll=") != -1:
            latitude = text.split("ll=")[1].split(",")[0]
            longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"
    if line.find("520 E") != -1:
        street_address = " ".join(line.split(",")[0].split()[:-1]).strip()
        city = "".join(line.split(",")[0].split()[-1]).strip()
        state = line.split(",")[1].strip()
        postal = line.split(",")[2].strip()
    location_type = "<MISSING>"
    hours_of_operation = (
        tree.xpath(
            '//div[./div/h4[contains(text(), "Location")]]/following-sibling::div//ul/li/span/text()'
        )
        or "<MISSING>"
    )
    if hours_of_operation == "<MISSING>":
        hours_of_operation = tree.xpath(
            '//div[./div/h4[contains(text(), "Ruffit")]]/following-sibling::div//ul/li/span/text()'
        )
    hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
    hours_of_operation = " ".join(hours_of_operation)
    cms = "".join(tree.xpath('//h3[contains(text(), "Coming")]/text()'))
    if cms:
        hours_of_operation = "Coming Soon"
    if hours_of_operation == "Coming Soon":
        latitude, longitude = "<MISSING>", "<MISSING>"
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
