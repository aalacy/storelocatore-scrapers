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
    r = session.get("https://www.bristolcountysavings.com/about-us/hours-locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//li/a[contains(@href, '/location')]/@href")


def get_data(url):
    locator_domain = "https://www.bristolcountysavings.com/"
    page_url = url

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = tree.xpath('//div[@class="location__info"]')
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
    for h in text:
        line = "".join(h.xpath('./p[@class="location__address"]/text()'))
        a = usaddress.tag(line, tag_mapping=tag)[0]

        street_address = (
            f"{a.get('address1')} {a.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = "".join(a.get("city"))
        state = "".join(a.get("state"))
        postal = "".join(a.get("postal"))
        country_code = "US"
        page_url = url

        store_number = "<MISSING>"
        location_name = "".join(
            h.xpath('//section[@class="location__meta clearfix"]/h1/text()')
        )
        phone = "".join(h.xpath('./p[@class="location__phone"]/text()')) or "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        _tmp = []
        days = tree.xpath(
            "//div[@class='location__row location__row--header']/span/text()"
        )[1:]
        times = tree.xpath("//div[@class='location__row'][1]/span/text()")[1:]

        for d, t in zip(days, times):
            _tmp.append(f"{d.strip()}: {t.strip()}")

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
