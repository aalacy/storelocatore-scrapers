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

    locator_domain = "https://jrecksubs.com"
    page_url = "https://jrecksubs.com/Location.html"

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
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    div = tree.xpath('//span[@class="style32"]')

    for d in div:
        adr = "".join(d.xpath(".//text()")).replace("Â", "").split("\n")
        for i in adr:
            if (
                "SYRACUSE AREA" in i
                or "WATERTOWN AREA" in i
                or "NORTHERN NEW YORK AREA" in i
            ):
                continue
            if not i:
                continue
            i = (
                i.replace("  ", " ")
                .replace("    ", " ")
                .replace("    ", " ")
                .replace("   ", " ")
                .split()
            )
            adr = " ".join(i[:-1])
            a = usaddress.tag(adr, tag_mapping=tag)[0]
            location_name = "Jreck Sub"
            location_type = "<MISSING>"
            street_address = f"{a.get('address1')} {a.get('address2')}".replace(
                "None", ""
            ).strip()
            phone = "".join(i[-1])
            state = a.get("state") or "<MISSING>"
            postal = a.get("postal") or "<MISSING>"
            country_code = "US"
            city = a.get("city") or "<MISSING>"
            if city.find("(") != -1:
                street_address = adr.split(" - ")[0].strip()
                city = adr.split(" - ")[1].split(",")[0].strip()
            store_number = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = "<MISSING>"

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
