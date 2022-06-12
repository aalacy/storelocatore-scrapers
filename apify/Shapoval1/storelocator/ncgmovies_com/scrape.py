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
    locator_domain = "https://ncgmovies.com"
    page_url = "https://ncgmovies.com/locations/"
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
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.content)
    li = tree.xpath("//div[./div/div/div/p]")
    for j in li:

        title = "".join(j.xpath(".//div[.//strong]//strong/text()"))
        location_name = "".join(
            j.xpath('.//div[2]//div[@class="fl-rich-text"]/p/text()[1]')
        )
        line = (
            " ".join(j.xpath('.//div[2]//div[@class="fl-rich-text"]/p/text()[2]'))
            .replace("\n", "")
            .replace("SWSuite", "SW Suite")
            .strip()
        )
        if line.find("160") != -1 or line.find("2125") != -1:
            line = (
                line
                + " "
                + "".join(j.xpath('.//div[2]//div[@class="fl-rich-text"]/p/text()[3]'))
                .replace("\n", "")
                .strip()
            )
        phone = (
            "".join(j.xpath('.//div[3]//div[@class="fl-rich-text"]/p/text()[1]'))
            .replace("Showtimes:", "")
            .replace("Phone:", "")
            .replace("Showtimes", "")
            .strip()
        )

        a = usaddress.tag(line, tag_mapping=tag)[0]

        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = a.get("city") or "<MISSING>"
        if line.find("2500") != -1:
            street_address = " ".join(line.split("MI")[0].split()[:-1])
            city = line.split("MI")[0].split()[-1].replace(",", "").strip()
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        if title.find("COMING SOON") != -1:
            hours_of_operation = "COMING SOON"
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
