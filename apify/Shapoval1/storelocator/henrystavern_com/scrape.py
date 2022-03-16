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

    locator_domain = "https://henrystavern.com"
    api_url = "https://henrystavern.com/location.php"
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
        '//section[@id="staticbgalt"]//a[@class="btn btn-block btn-default brdr"]'
    )
    for d in div:
        slug = (
            "".join(d.xpath(".//@href"))
            .replace(".", "")
            .strip()
            .replace("locationphp", "location.php")
        )

        page_url = f"{locator_domain}{slug}"
        location_name = "".join(d.xpath(".//text()"))
        slug_loc_name = (
            location_name.replace(" ", "").lower().replace("pdx", "PDX").strip()
        )
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ad = "".join(
            tree.xpath(
                '//div[@class="col-sm-8 col-md-9 col-lg-9 pt15 pb15 lead cWhite text-right"]/span//text()'
            )
        ).strip()
        if ad.find("Located") != -1:
            ad = ad.split("Located")[0].strip()
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        state = a.get("state")
        postal = a.get("postal")
        country_code = "US"
        city = a.get("city")
        store_number = "<MISSING>"
        phone = "".join(tree.xpath('//span[@class="lead strong"]/text()'))
        hours_of_operation = (
            "".join(tree.xpath('//h3[text()="HOURS"]/following::p[1]//text()'))
            .replace("\r\n", " ")
            .replace("AIRPORT HOURS", "")
            .strip()
        )
        if hours_of_operation.find("*") != -1:
            hours_of_operation = hours_of_operation.split("*")[0].strip()
        latitude = (
            "".join(tree.xpath('//script[contains(text(), "var cities")]/text()'))
            .split(f"{slug_loc_name}")[1]
            .split(",")[1]
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "var cities")]/text()'))
            .split(f"{slug_loc_name}")[1]
            .split(",")[2]
            .split("]")[0]
            .strip()
        )
        location_type = "<MISSING>"

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
