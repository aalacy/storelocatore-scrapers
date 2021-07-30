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

    locator_domain = "https://www.rocknjoe.com"
    page_url = "https://www.rocknjoe.com/locations"
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
    div = tree.xpath('//div[./h6//span[text()="Hours"]]')

    for d in div:

        location_type = "Rock 'n' Joe Coffee"
        adr = d.xpath(
            './/preceding-sibling::div[./p[@style="line-height:1.7em;font-size:17px"]][1]//text()'
        )
        ad = list(filter(None, [a.strip() for a in adr]))
        adress = " ".join(ad[:-1])
        if "".join(ad).find("Clinic") != -1:
            adress = " ".join(ad)
        a = usaddress.tag(adress, tag_mapping=tag)[0]
        phone = "".join(adr[-1])
        if "".join(adr).find("420") != -1:
            phone = "<MISSING>"
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        location_name = (
            "".join(d.xpath(".//preceding-sibling::div[5]/h6//text()")) or "<MISSING>"
        )
        if location_name == "<MISSING>":
            location_name = "".join(d.xpath(".//preceding-sibling::div[3]/h6//text()"))
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        days = d.xpath(".//following-sibling::div[1]/p/span/text()")

        times = d.xpath(".//following-sibling::div[2]/p/span/text()") or "<MISSING>"
        if times == "<MISSING>":
            times = d.xpath(".//following::div[2]/p/span/text()")
        _tmp = []
        if days != "<MISSING>" and times != "<MISSING>":
            for d, t in zip(days, times):
                _tmp.append(f"{d.strip()}: {t.strip()}")
        hours_of_operation = " ".join(_tmp) or "<MISSING>"

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
