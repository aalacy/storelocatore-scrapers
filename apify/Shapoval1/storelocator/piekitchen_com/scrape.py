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
    locator_domain = "https://piekitchen.com"
    page_url = "https://piekitchen.com/locations/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://piekitchen.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
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
    div = tree.xpath('//div[@class="location"]')
    for d in div:
        line = (
            " ".join(d.xpath('.//div[@class="right"]/p/text()'))
            .replace("\n", "")
            .replace("(", "")
            .strip()
        )
        if line.find("Weston") != -1:
            line = line.split("Pointe")[1].strip()
        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = a.get("city")
        postal = a.get("postal")
        state = a.get("state")
        phone = (
            "".join(d.xpath('.//a[contains(@href, "tel")]/text()')).strip()
            or "<MISSING>"
        )
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "".join(d.xpath('.//h2[@class="maroon"]/text()'))
        ll = "".join(d.xpath(".//h5/following-sibling::iframe/@src"))
        ll = ll.split("!2d")[1].split("!2m")[0].replace("!3d", ",")
        latitude = ll.split(",")[1]
        longitude = ll.split(",")[0]
        location_type = "<MISSING>"
        tmp = []
        days = d.xpath(
            './/strong[contains(text(), "Hours")]/following-sibling::div[@class="hour"]/div[@class="days"]//text()'
        )
        days = list(filter(None, [a.strip() for a in days]))
        time = d.xpath(
            './/strong[contains(text(), "Hours")]/following-sibling::div[@class="hour"]/div[@class="hours-item"]//text()'
        )
        time = list(filter(None, [a.strip() for a in time]))
        for d, t in zip(days, time):
            tmp.append(f"{d.strip()} {t.strip()}")
        hours_of_operation = ";".join(tmp) or "Coming soon"
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
