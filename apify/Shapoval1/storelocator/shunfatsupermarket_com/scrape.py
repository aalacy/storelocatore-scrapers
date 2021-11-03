import csv
import usaddress
from lxml import html
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


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get(
        "http://www.shunfatsupermarket.com/find-a-location/", headers=headers
    )

    tree = html.fromstring(r.content)

    return tree.xpath(
        "//div[@class='avia_mega_div avia_mega3 nine units']//ul[@class='sub-menu']/li[contains(@id, 'menu-item')]/a/@href"
    )


def get_data(url):
    locator_domain = "http://www.shunfatsupermarket.com/"
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
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)

    line = " ".join(
        tree.xpath('//div[@class="av-subheading av-subheading_below  "]/p/text()')
    )
    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2')}".replace(
        "None", ""
    ).strip()
    city = a.get("city")
    postal = a.get("postal")
    state = a.get("state")
    country_code = "US"
    store_number = "<MISSING>"
    location_name = "".join(
        tree.xpath(
            '//h2[@itemprop="headline"]/text() | //div[@class="av-special-heading av-special-heading-h3  blockquote modern-quote  avia-builder-el-2  el_before_av_hr  avia-builder-el-first   "]/h3/text() | //div[@class="av-special-heading av-special-heading-h3  blockquote modern-quote  avia-builder-el-2  el_before_av_hr  avia-builder-el-first  "]/h3/text()'
        )
    )
    phone = (
        "".join(
            tree.xpath(
                '//header[@class="entry-content-header"]/div[contains(text(), "Tel")]/text()'
            )
        )
        .replace("Tel:", "")
        .strip()
    )
    latitude = (
        "".join(tree.xpath('//script[@class="av-php-sent-to-frontend"]/text()'))
        .split("['lat'] =")[1]
        .split(";")[0]
        .strip()
    )
    longitude = (
        "".join(tree.xpath('//script[@class="av-php-sent-to-frontend"]/text()'))
        .split("['long'] =")[1]
        .split(";")[0]
        .strip()
    )
    location_type = "<MISSING>"
    hours_of_operation = (
        "".join(
            tree.xpath(
                '//header[@class="entry-content-header"]/div[contains(text(), "Hours")]/text() | //div[contains(text(), "AM")]/text()'
            )
        )
        .replace("Hours:", "")
        .strip()
        or "<MISSING>"
    )
    if phone.find("TBD") != -1 and hours_of_operation.find("TBD") != -1:
        phone = "<MISSING>"
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
