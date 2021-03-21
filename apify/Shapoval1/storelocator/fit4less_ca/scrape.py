import csv
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
    r = session.get("https://www.fit4less.ca/sitemap-en.xml")
    tree = html.fromstring(r.content)
    return tree.xpath(
        "//url/loc[contains(text(), 'province')]/text() | //url/loc[contains(text(), 'british')]/text()"
    )


def get_data(url):
    locator_domain = "https://www.fit4less.ca"
    page_url = "".join(url)
    if page_url.count("/") < 7 and page_url.find("british") == -1:
        return
    if (
        page_url.find("british")
        and page_url.count("/") != 5
        and page_url.find("province") == -1
    ):
        return
    if (
        page_url
        == "https://www.fit4less.ca/gym-memberships/locations/provinces/ontario/stratford"
    ):
        return
    if (
        page_url
        == "https://www.fit4less.ca/memberships/locations/provinces/ontario/niagara-falls"
    ):
        return
    if (
        page_url
        == "https://www.fit4less.ca/memberships/locations/provinces/nova-scotia/dartmouth"
    ):
        return
    if (
        page_url
        == " https://www.fit4less.ca/memberships/locations/provinces/ontario/bowmanville"
    ):
        return
    if (
        page_url
        == "https://www.fit4less.ca/memberships/locations/provinces/ontario/bowmanville"
    ):
        return
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
    line = (
        " ".join(tree.xpath('//div[@class="gym-details-info__address"]//text()'))
        .replace("\n", "")
        .strip()
    )
    # a = usaddress.tag(line, tag_mapping=tag)[0]

    store_number = "<MISSING>"
    location_name = "".join(tree.xpath('//h1[@class="gym__details--h1"]//text()'))
    phone = (
        "".join(
            tree.xpath(
                '//div[@class="gym-details-info__address"]/following-sibling::div[1][@class="gym-details-info__phone"]/a/text()'
            )
        )
        or "<MISSING>"
    )
    text = "".join(tree.xpath('//div[@class="gym-details-info__directions"]/a/@href'))
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    postal = "<MISSING>"
    country_code = "<MISSING>"
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
    hours_of_operation = tree.xpath('//span[@class="hours-hours"]/div//text()')
    hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
    hours_of_operation = ";".join(hours_of_operation).replace(":;", ":")
    block = (
        "{" + "".join(tree.xpath('//script[@type="application/ld+json"]/text()')) + "}"
    )
    if block.find('"streetAddress": "') != -1:
        street_address = block.split('"streetAddress": "')[1].split('"')[0]
    if block.find('"addressLocality": "') != -1:
        city = block.split('"addressLocality": "')[1].split('"')[0]
    if block.find('"addressRegion": "') != -1:
        state = block.split('"addressRegion": "')[1].split('"')[0]
    if block.find('"postalCode": "') != -1:
        postal = block.split('"postalCode": "')[1].split('"')[0]
    if block.find('"addressCountry": "') != -1:
        country_code = block.split('"addressCountry": "')[1].split('"')[0]
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
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
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
