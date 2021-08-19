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

    locator_domain = "https://www.fitzoneforwomen.com"
    api_url = "https://www.fitzoneforwomen.com/locations/"
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
    div = tree.xpath(
        '//a[./span[contains(text(), "Locations")]]/following-sibling::div//ul/li/a'
    )

    for d in div:
        page_url = "".join(d.xpath(".//@href"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath('//h3[@class="vc_custom_heading"]/text()'))
        ad = " ".join(
            tree.xpath('//h3/following-sibling::p[@class="vc_custom_heading"]/text()')
        ).replace("(M120)", "M120")

        if ad.find("Telephone:") != -1:
            ad = ad.split("Telephone:")[0].strip()
        if ad.find("Phone") != -1:
            ad = ad.split("Phone")[0].strip()
        if ad.find("Phone:") != -1:
            ad = ad.split("Phone:")[0].strip()
        if ad.find("(") != -1:
            ad = ad.split("(")[0].strip()
        if ad.find("– 337") != -1:
            ad = ad.split("– 337")[0].strip()
        ad = ad.replace(" – ", "-").replace(" –", "").replace("-", " – ")
        a = usaddress.tag(ad, tag_mapping=tag)[0]

        location_type = "<MISSING>"
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        phone = " ".join(
            tree.xpath('//h3/following-sibling::p[@class="vc_custom_heading"]/text()')
        )
        if phone.find("Contact") != -1:
            phone = phone.split("Contact")[0].strip()
        phone = phone.replace(") ", ")-").split()[-1].strip()
        state = a.get("state")
        postal = a.get("postal")
        country_code = "US"
        city = a.get("city")
        store_number = "<MISSING>"
        map_link = "".join(tree.xpath('//iframe[contains(@src, "google.com")]/@src'))
        try:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        if page_url.find("mattawan-michigan/") != -1:
            latitude = (
                "".join(tree.xpath("//iframe/@src"))
                .split("ll=")[1]
                .split("&")[0]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath("//iframe/@src"))
                .split("ll=")[1]
                .split("&")[0]
                .split(",")[1]
                .strip()
            )
        hours_of_operation = tree.xpath(
            '//*[contains(text(), "Staffed Hours:")]/following-sibling::ul[1]//text() | //*[contains(text(), "Open 24")]/following-sibling::ul[1]//text() | //*[contains(text(), "New Summer Hours")]/following-sibling::ul[1]//text()'
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation) or "<MISSING>"

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
