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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(
        "https://www.themaxchallenge.com/max-challenge-locations/?address[0]&post[0]=max-location&per_page=70&lat&lng&form=1&action=fs&is_skip=true",
        headers=headers,
    )
    tree = html.fromstring(r.text)
    return tree.xpath(
        '//li[./div[@class="wppl-title-holder"]]//h2[@class="wppl-h2"]/a/@href'
    )


def get_data(url):
    locator_domain = "https://www.themaxchallenge.com/"
    page_url = url
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath('//div[@class="header-location-name"]/span/text()')
    )
    ad = (
        "".join(
            tree.xpath('//div[@class="gmw-phone"]/following-sibling::div[1]//a/text()')
        )
        or "<MISSING>"
    )
    if ad == "<MISSING>":
        ad = "".join(
            tree.xpath(
                '//div[@class="gmw-single-post-contact"]/preceding-sibling::div[1]//a/text()'
            )
        )

    a = usaddress.tag(ad, tag_mapping=tag)[0]
    street_address = (
        f"{a.get('address1')} {a.get('address2')}".replace("None", "").strip()
        or "<MISSING>"
    )
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    if state.find(",") != -1:
        state = state.split(",")[0].strip()
    postal = a.get("postal") or "<MISSING>"
    country_code = "USA"
    store_number = "<MISSING>"
    phone = (
        " ".join(
            tree.xpath(
                '//div[@class="gmw-single-post-sc-header"]/following-sibling::div//a[contains(@href, "tel")]/text()'
            )
        )
        or "<MISSING>"
    )
    if phone.find("USA") != -1:
        phone = phone.split("1621")[0].strip()
    location_type = "<MISSING>"
    hours_of_operation = "<MISSING>"

    latitude = (
        "".join(tree.xpath('//script[contains(text(), "gmwSinglePostMap ")]/text()'))
        .split("LatLng(")[1]
        .split(",")[0]
        .strip()
    )
    longitude = (
        "".join(tree.xpath('//script[contains(text(), "gmwSinglePostMap ")]/text()'))
        .split("LatLng(")[1]
        .split(",")[1]
        .split(")")[0]
        .strip()
    )
    cms = "".join(tree.xpath('//h2[@class="text-center banner-title"]/text()'))
    if "Coming Soon" in cms:
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
