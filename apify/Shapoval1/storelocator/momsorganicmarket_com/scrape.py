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
    locator_domain = "https://momsorganicmarket.com/"
    api_url = "https://momsorganicmarket.com/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    page_urls = tree.xpath('//ul[@id="top-menu"]/li[1]/ul[1]/li/a/@href')
    for i in page_urls:
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
        subr = session.get(i)
        trees = html.fromstring(subr.text)
        block = trees.xpath('//div[@class="et_pb_blurb_container"]')

        for b in block:
            ad = "".join(
                b.xpath(
                    './/div[contains(@class,"et_pb_blurb_description")]/p[2]/text()'
                )
            )
            a = usaddress.tag(ad, tag_mapping=tag)[0]
            street_address = f"{a.get('address1')} {a.get('address2')}".replace(
                "None", ""
            ).strip()

            city = a.get("city")
            state = a.get("state")
            postal = a.get("postal")
            country_code = "US"

            store_number = "<MISSING>"
            page_url = "".join(b.xpath(".//h1/a/@href"))
            location_name = "".join(b.xpath(".//h1//text()"))
            phone = "".join(b.xpath(".//a[contains(@href, 'tel')]/text()"))
            location_type = "<MISSING>"
            hours_of_operation = b.xpath(
                ".//a[contains(@href, 'tel')]/following::p[1]//text()"
            )
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = " ".join(hours_of_operation).replace(",", "")
            if street_address.find("83 Stanley Ave") != -1:
                phone = "".join(
                    b.xpath(".//div[@class='et_pb_blurb_description']/p[4]/text()")
                )
                hours_of_operation = b.xpath(
                    ".//div[@class='et_pb_blurb_description']/p[6]//text()"
                )
                hours_of_operation = list(
                    filter(None, [a.strip() for a in hours_of_operation])
                )
                hours_of_operation = " ".join(hours_of_operation).replace(",", "")

            hours_of_operation = hours_of_operation.replace("\n", " ").strip()
            session = SgRequests()
            rr = session.get(page_url)
            ttree = html.fromstring(rr.text)
            text = "".join(ttree.xpath(".//a[1][contains(@href, 'google')]/@href"))
            try:
                if text.find("ll=") != -1:
                    latitude = text.split("ll=")[1].split(",")[0]
                    longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
                else:
                    latitude = text.split("@")[1].split(",")[0]
                    longitude = text.split("@")[1].split(",")[1]
            except IndexError:
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
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
