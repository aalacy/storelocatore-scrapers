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
    locator_domain = "https://myrosatis.com"
    api_url = "https://myrosatis.com/locations/all-locations/"

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
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath('//a[contains(text(), "More Details")]')

    for b in block:
        page_url = "".join(b.xpath(".//@href"))
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ad = (
            "".join(tree.xpath('//span[@class="location"]/text()'))
            .replace("(", "")
            .replace(")", "")
            .strip()
        )
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = a.get("city") or "<MISSING>"
        state = a.get("state")
        postal = a.get("postal")
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        location_name = "".join(
            tree.xpath('//div[@class="section-body-location"]//h2/text()')
        )
        phone = (
            "".join(tree.xpath('//p[contains(text(), "Phone")]/text()'))
            .replace("Phone:", "")
            .strip()
            or "<MISSING>"
        )
        ll = "".join(tree.xpath('//a[contains(text(), "map it")]/@href'))
        latitude = ll.split("loc:")[1].split(",")[0]
        longitude = ll.split("loc:")[1].split(",")[1]
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[@class="section-body-location"]//p[contains(text(), "pm")]/text() | //div[contains(text(), "pm")]/text() | //div[@class="section-body-location"]//p[contains(text(), "am")]/text() | //p/span[@class="s1"]/text() | //div[@class="section-body-location"]//p[contains(text(), "Closed")]/text() | //i[contains(text(), "temporarily adjusted our hours")]/text() | //div[@class="section-body-location"]//p[contains(text(), "AM")]/text() | //div[@class="section-body-location"]//p[contains(text(), "p.m.")]/text() | //p[contains(text(), "Dine-In Hours:")]/text() | //li[contains(text(), "am")]/text() | //p[contains(text(), "OPEN DAILY")]/text()'
                )
            )
            .replace("\n", "")
            .replace("Dine-In Hours:", "")
            .replace("Open", "")
            .replace("ONLY", "")
            .replace("&", "-")
            .replace("Hamburger", "")
            .replace("Every Day", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation.find("1/3") != -1:
            hours_of_operation = hours_of_operation.split("1/3")[0].strip()
        if hours_of_operation.find("$") != -1:
            hours_of_operation = hours_of_operation.split("$")[0].strip()
        if hours_of_operation.find("Purchase") != -1:
            hours_of_operation = hours_of_operation.split("Purchase")[0].strip()
        if hours_of_operation.find("Two") != -1:
            hours_of_operation = hours_of_operation.split("Two")[0].strip()
        if hours_of_operation.find("Controlling") != -1:
            hours_of_operation = hours_of_operation.split("Controlling")[0].strip()
        if hours_of_operation.find("We have temporarily adjusted our hours to") != -1:
            hours_of_operation = hours_of_operation.split(
                "We have temporarily adjusted our hours to"
            )[1].strip()
        if hours_of_operation.find("Off") != -1:
            hours_of_operation = hours_of_operation.split("Off")[0].strip()
        if hours_of_operation.find("Understand") != -1:
            hours_of_operation = hours_of_operation.split("Understand")[0].strip()
        if hours_of_operation.find("Familiar") != -1:
            hours_of_operation = hours_of_operation.split("Familiar")[0].strip()
        if hours_of_operation.find("Must") != -1:
            hours_of_operation = hours_of_operation.split("Must")[0].strip()

        if phone.find("COMING SOON!") != -1:
            phone = "<MISSING>"
            hours_of_operation = "COMING SOON"
        if phone.find("TEMPORARILY CLOSED") != -1:
            hours_of_operation = "TEMPORARILY CLOSED"
            phone = "<MISSING>"
        if phone.find("Temporarily Closed") != -1:
            hours_of_operation = "Temporarily Closed"
            phone = "<MISSING>"

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
