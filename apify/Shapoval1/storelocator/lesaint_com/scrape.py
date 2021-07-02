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

    locator_domain = "https://www.lesaint.com/"
    api_url = (
        "https://www.lesaint.com/warehouse-ecommerce-fulfillment-centers-locations/"
    )
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
        '//div[./p//a[text()="Get Directions"]] | //div[./p//a[text()="Get Direction"]]'
    )
    s = set()
    for d in div:
        ad = d.xpath(".//p//text()")

        ad = list(filter(None, [a.strip() for a in ad]))

        ad = (
            " ".join(ad)
            .replace("Get Directions", "")
            .replace("OH,", "OH")
            .replace("Boulevard,", "Boulevard")
            .replace("6044 0", "60440")
        )

        if ad.find("TAGG Logistics") != -1:
            ad = ad.split("TAGG Logistics")[1].strip()
        if ad.count(",") == 2:
            ad = " ".join(ad.split(",")[1:]).split()[1:]
            ad = " ".join(ad)

        a = usaddress.tag(ad, tag_mapping=tag)[0]
        page_url = (
            "".join(d.xpath('.//a[contains(@href, "www.tagglogistics.com")]/@href'))
            or "<MISSING>"
        )
        if page_url == "<MISSING>":
            page_url = "https://www.lesaint.com/warehouse-ecommerce-fulfillment-centers-locations/"
        if ad.find("2850 Marquis Drive") != -1:
            page_url = "https://www.tagglogistics.com/dallas-tx-order-fulfillment-center-garland-texas/"
        location_name = "".join(
            d.xpath(
                './/span[@class="location-name"]/text() | .//span[./strong]/strong/text() | .//span[./a]/a/text() | .//a[./span]/span/text()'
            )
        )
        if ad.find("13204 ") != -1:
            location_name = "Los Angeles, CA"

        location_type = "<MISSING>"
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        city = a.get("city") or "<MISSING>"

        store_number = "<MISSING>"
        text = "".join(d.xpath('.//a[text()="Get Directions"]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        if page_url.find("tagglogistics") != -1:
            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            phone = " ".join(tree.xpath("//*//strong/a/text()")).split()[0].strip()

        line = street_address
        if line in s:
            continue
        s.add(line)

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
