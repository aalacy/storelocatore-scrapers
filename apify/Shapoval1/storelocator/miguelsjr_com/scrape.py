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
    r = session.get("https://www.miguelsjr.com/location-sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc/text()")


def get_data(url):
    locator_domain = "https://www.miguelsjr.com"
    page_url = "".join(url)
    if page_url == "https://www.miguelsjr.com/location/":
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    line = "".join(tree.xpath('//div[@class="group addy"]/a/text()'))
    a = usaddress.tag(line, tag_mapping=tag)[0]

    street_address = f"{a.get('address1')} {a.get('address2')}".replace(
        "None", ""
    ).strip()
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    if state.find(",") != -1:
        state = state.split(",")[0]
    postal = a.get("postal") or "<MISSING>"
    country_code = "US"

    store_number = "<MISSING>"
    location_name = "".join(
        tree.xpath('//div[@class="top"]/div[@class="title"]/text()')
    )
    phone = "".join(
        tree.xpath(
            '//h5[contains(text(), "Phone")]/following-sibling::a[contains(@href, "tel")]/text()'
        )
    )
    latitude = "".join(tree.xpath('//a[contains(text(), "Set as my store")]/@data-lat'))
    longitude = "".join(
        tree.xpath('//a[contains(text(), "Set as my store")]/@data-lon')
    )
    location_type = "<MISSING>"
    tmp = []
    hours1 = tree.xpath(
        '//h5[contains(text(), "Store Hours")]/following-sibling::table//tr/td[1]/text()'
    )
    hours2 = tree.xpath(
        '//h5[contains(text(), "Store Hours")]/following-sibling::table//tr/td[2]/text()'
    )
    hours3 = tree.xpath(
        '//h5[contains(text(), "Store Hours")]/following-sibling::table//tr/td[3]/text()'
    )
    for d, t, l in zip(hours1, hours2, hours3):
        tmp.append(f"{d.strip()} {t.strip()} - {l.strip()}")
    hours_of_operation = " ".join(tmp)

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
