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

    locator_domain = "https://www.garfieldsrestaurant.com/"
    api_url = "https://www.garfieldsrestaurant.com/bot.ashx?url=https://www.garfieldsrestaurant.com/pgv2.aspx?id=e1639645-3cfc-4061-82dc-342f8eb84149&_=1626122576666"
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
    div = tree.xpath('//div[@class="cta-wrap cb-change-width  js-item"]/a')

    for d in div:

        page_url = "https:" + "".join(d.xpath(".//@href"))

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ad = tree.xpath('//div[./div[@class="row js-group-row"]]//text()')
        ad = list(filter(None, [a.strip() for a in ad]))
        location_name = "".join(ad[2])

        adr = (
            " ".join(ad[3:])
            .replace("\r", "")
            .replace("\xa0", "")
            .split("Get")[0]
            .strip()
        )
        address = " ".join(adr.split()[:-1])
        a = usaddress.tag(address, tag_mapping=tag)[0]
        location_type = "Restaurant"
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        city = a.get("city") or "<MISSING>"
        store_number = "<MISSING>"
        text = "".join(tree.xpath('//a[contains(@href, "maps")]/@href'))
        if "Selinsgrove" in location_name:
            text = "".join(tree.xpath('//a[./span[text()="Directions"]]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = adr.split()[-1].strip()
        hours_of_operation = (
            " ".join(ad[3:])
            .replace("\r", "")
            .replace("\xa0", "")
            .split("ours")[1]
            .split("Let's")[0]
            .replace("Less", "")
            .replace("SUNDAY - THURSDAY 11 AM - 9PM FRIDAY - SATURDAY", "")
            .strip()
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
