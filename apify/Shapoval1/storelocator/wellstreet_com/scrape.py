import csv
import usaddress
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


def fetch_data():
    out = []

    locator_domain = "https://www.wellstreet.com"
    api_url = "https://www.wellstreet.com/region/"
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
    r = session.post(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//p/a[contains(@href, "/region/")]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        urls = f"{locator_domain}{slug}"
        session = SgRequests()
        r = session.get(urls, headers=headers)
        tree = html.fromstring(r.text)
        li = tree.xpath('//div[@class="map-list-item"]')
        s = set()
        for l in li:

            page_url = "".join(l.xpath('.//a[@class="title"]/@href'))
            location_name = "".join(l.xpath('.//a[@class="title"]/text()'))
            hours_of_operation = (
                " ".join(l.xpath('.//div[@class="more-hours mt-2"]/text()'))
                .replace("\r\n", " ")
                .strip()
            )

            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            ad = (
                tree.xpath(
                    '//div[@class="row row-address mb-3"]//a/text() | //i[@class="fa fa-map-marker"]/following-sibling::text()'
                )
                or "<MISSING>"
            )
            ad = list(filter(None, [a.strip() for a in ad]))
            ad = (
                " ".join(ad)
                .replace("\t", "")
                .replace("\n", " ")
                .replace("\r", "")
                .strip()
            )
            a = usaddress.tag(ad, tag_mapping=tag)[0]
            street_address = f"{a.get('address1')} {a.get('address2')}".replace(
                "None", ""
            ).strip()
            phone = (
                "".join(
                    tree.xpath(
                        '//div[@class="row row-phone mb-3"]//a/text() | //p[@class="ffb-id-3i3ka4b8 fg-text-dark"]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            try:
                ll = (
                    "".join(tree.xpath('//script[contains(text(), "LatLng")]/text()'))
                    .split("LatLng(")[1]
                    .split(")")[0]
                    .strip()
                    or "<MISSING>"
                )
            except:
                ll = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            if ll != "<MISSING>":
                latitude = ll.split(",")[0]
                longitude = ll.split(",")[1]
            if latitude == "<MISSING>" and longitude == "<MISSING>":
                latitude = "".join(
                    tree.xpath(f'//div[./p[contains(text(), "{phone}")]]/@data-lat')
                )
                longitude = "".join(
                    tree.xpath(f'//div[./p[contains(text(), "{phone}")]]/@data-lng')
                )
            location_type = "urgent care"
            state = a.get("state") or "<MISSING>"
            postal = a.get("postal") or "<MISSING>"
            country_code = "US"
            city = a.get("city") or "<MISSING>"
            store_number = "<MISSING>"

            line = street_address
            if line in s:
                continue
            s.add(line)

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


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
