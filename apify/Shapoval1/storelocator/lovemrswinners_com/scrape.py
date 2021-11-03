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
    locator_domain = "https://lovemrswinners.com"
    api_url = "https://lovemrswinners.com/locations/"

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
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[@class="col-md-4 text-center"]/p[./text()]')
    for j in block:
        ad = " ".join(j.xpath(".//text()"))
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        page_url = (
            "".join(
                j.xpath(
                    './/following-sibling::a[1][contains(text(), "View Store")]/@href'
                )
            )
            or "https://lovemrswinners.com/locations/"
        )
        if page_url != "https://lovemrswinners.com/locations/":
            page_url = f"https://lovemrswinners.com{page_url}"
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = a.get("city")
        postal = a.get("postal") or "<MISSING>"
        state = a.get("state")
        if street_address.find("1100") != -1:
            street_address = " ".join(ad.split(",")[0].split()[:-1])
            city = "".join(ad.split(",")[0].split()[-1])
            state = "".join(ad.split(",")[1]).strip()
        phone = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        location_name = state
        country_code = "US"
        store_number = "<MISSING>"
        if page_url != "https://lovemrswinners.com/locations/":

            session = SgRequests()
            r = session.get(page_url)
            trees = html.fromstring(r.text)
            country_code = "US"
            store_number = "<MISSING>"
            location_name = (
                "".join(trees.xpath('//div[@class="slide-caption-2"]//text()'))
                .split("WELCOME TO")[1]
                .strip()
            )
            phone = (
                "".join(trees.xpath('//div[@class="phone"]/text()'))
                .replace("\n", "")
                .strip()
            )
            text = "".join(trees.xpath('//a[@class="map-direction-btn"]/@href'))
            try:
                if text.find("ll=") != -1:
                    latitude = text.split("ll=")[1].split(",")[0]
                    longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
                else:
                    latitude = text.split("@")[1].split(",")[0]
                    longitude = text.split("@")[1].split(",")[1]
            except IndexError:
                latitude, longitude = "<MISSING>", "<MISSING>"

            location_type = "<MISSING>"
            hours_of_operation = (
                "".join(trees.xpath('//div[@class="hours"]//text()'))
                .replace("\n", "")
                .strip()
            )
            if hours_of_operation.find("COME JOIN US!") != -1:
                hours_of_operation = hours_of_operation.split("COME JOIN US!")[
                    1
                ].strip()
            if hours_of_operation.find("Lobby closes") != -1:
                hours_of_operation = hours_of_operation.split("Lobby closes")[0].strip()
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
