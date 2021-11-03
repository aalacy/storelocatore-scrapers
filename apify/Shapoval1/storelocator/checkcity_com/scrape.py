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

    locator_domain = "https://www.checkcity.com"
    api_url = "https://www.checkcity.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[text()="Store Locations"]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        spage_url = f"{locator_domain}{slug}"

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

        r = session.get(spage_url, headers=headers)
        tree = html.fromstring(r.text)

        block = tree.xpath("//p[./a]")
        for b in block:
            sslug = "".join(b.xpath(".//a/@href"))
            page_url = f"{locator_domain}{sslug}"

            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            location_name = (
                "".join(tree.xpath('//div[@class="check-city-state"]/div/text()'))
                .replace("|", "")
                .replace("\n", "")
                .strip()
            )
            ad = "".join(
                tree.xpath('//div[text()="Address: "]/following-sibling::div[1]/text()')
            )
            a = usaddress.tag(ad, tag_mapping=tag)[0]
            location_type = "<MISSING>"
            street_address = f"{a.get('address1')} {a.get('address2')}".replace(
                "None", ""
            ).strip()
            phone = "".join(
                tree.xpath(
                    '//div[text()="Phone Number:"]/following-sibling::div[1]/text()'
                )
            )
            state = a.get("state") or "<MISSING>"
            postal = a.get("postal") or "<MISSING>"
            country_code = "US"
            city = a.get("city") or "<MISSING>"
            store_number = "<MISSING>"
            map_link = "".join(tree.xpath("//iframe/@src"))
            try:
                latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
            if latitude == "<MISSING>":
                latitude = map_link.split("@")[1].split(",")[0].strip()
                longitude = map_link.split("@")[1].split(",")[1].strip()
            hours_of_operation = tree.xpath(
                '//div[text()="Hours:"]/following-sibling::div[1]//text()'
            )
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = (
                " ".join(hours_of_operation)
                .replace("â", "-")
                .replace("Â", "")
                .replace("  ", " ")
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
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
