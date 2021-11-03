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

    locator_domain = "https://www.delranchousa.com"
    api_url = "https://www.delranchousa.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABU0Wug"

    session = SgRequests()
    r = session.get(api_url)

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

    js = r.json()
    for j in js["markers"]:
        line = "".join(j.get("address"))
        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = a.get("city") or "<MISSING>"
        postal = a.get("postal")
        if street_address.find("462") != -1:
            postal = "73064"
        state = a.get("state")
        phone = j.get("description")
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "".join(j.get("title")).replace("<br>", "")
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        page_url = "https://www.delranchousa.com/locations/"
        if city == "<MISSING>":
            session = SgRequests()
            r = session.get(
                "https://delranchousa.com/locations/oklahoma-city-2741-ne-23rd/"
            )
            tree = html.fromstring(r.text)
            line = "".join(tree.xpath('//div[@class="fusion-text"]/p[1]/text()[2]'))
            a = usaddress.tag(line, tag_mapping=tag)[0]
            city = a.get("city")
            state = a.get("state")
            postal = a.get("postal")
            phone = "".join(tree.xpath("//p[./b]/text()"))
        if page_url == "https://www.delranchousa.com/locations/":
            session = SgRequests()
            r = session.get("https://www.delranchousa.com/locations/")
            tree = html.fromstring(r.text)
            block = tree.xpath('//p[./a[contains(text(), "Read More")]]')
            for b in block:
                slug = "".join(b.xpath("./text()")).replace("\n", "").split()[0].strip()
                if street_address.find(slug) != -1:
                    page_url = "".join(
                        b.xpath('./a[contains(text(), "Read More")]/@href')
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
