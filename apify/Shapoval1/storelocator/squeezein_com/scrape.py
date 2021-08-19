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

    locator_domain = "https://www.squeezein.com/"

    api_url = "https://www.squeezein.com/"
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
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath(
        '//a[./div/img] | //input[@name="mobile-folder-toggle-5616c882e4b036a0b93cb930"]/following-sibling::div/div/a[contains(text(), "Idaho")]'
    )
    for b in block:
        slug = "".join(b.xpath(".//@href"))
        page_url = "".join(slug)
        if page_url.find("https://www.squeezein.com") == -1:
            page_url = f"https://www.squeezein.com{slug}"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(
            tree.xpath(
                '//h1[@class="page-title"]/text() | //div[@id="block-b88126acbca38aeecc3f"]/div[@class="sqs-block-content"]/h2/text()'
            )
        )
        location_type = "<MISSING>"
        ad = " ".join(
            tree.xpath(
                '//h1[@class="page-title"]/following-sibling::div/h2/strong/text()'
            )
        )
        if (
            location_name.find("Truckee") != -1
            or location_name.find("Reno") != -1
            or location_name.find("Reno") != -1
            or location_name.find("Sparks") != -1
        ):
            ad = " ".join(
                tree.xpath(
                    '//h1[@class="page-title"]/following-sibling::div/p/strong/text()'
                )
            )
        if location_name.find("Modesto") != -1:
            ad = " ".join(
                tree.xpath(
                    '//h1[@class="page-title"]/following-sibling::div/p[1]/text()'
                )
            )
        if location_name.find("Carson") != -1:
            ad = " ".join(
                tree.xpath(
                    '//h1[@class="page-title"]/following-sibling::div/p[2]/text()'
                )
            )
        if page_url.find("chinohills") != -1:
            ad = " ".join(
                tree.xpath(
                    '//h1[@class="page-title"]/following-sibling::div/p[2]/text()'
                )
            )
        if page_url.find("freder") != -1:
            ad = (
                " ".join(
                    tree.xpath(
                        '//h1[@class="page-title"]/following-sibling::div/p[2]/text()'
                    )
                )
                + " "
                + " ".join(
                    tree.xpath(
                        '//h1[@class="page-title"]/following-sibling::div/p[3]/text()'
                    )
                )
            )
        if page_url.find("new-page") != -1:
            ad = " ".join(tree.xpath("//div/h2/following-sibling::p[2]/text()"))
        ad = ad.replace("CLOSED", "").strip()
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        phone = " ".join(
            tree.xpath(
                '//h2[contains(text(), "Phone")]//text() | //h3[contains(text(), "Phone")]//text()'
            )
        )
        if page_url.find("north") != -1:
            phone = " ".join(tree.xpath('//p[contains(text(), "PHONE:")]//text()'))
        if page_url.find("south") != -1 or page_url.find("sparks") != -1:
            phone = " ".join(tree.xpath('//h3[contains(text(), "PHONE:")]//text()'))
        if page_url.find("new-page") != -1:
            phone = " ".join(tree.xpath('//p[contains(text(), "Phone")]//text()'))
        if page_url.find("https://www.squeezein.com/las-vegas-nv-eastern") != -1:
            phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()'))
        if phone.find("PHONE:") != -1:
            phone = phone.replace("PHONE:", "").strip()
        if phone.find("Phone:") != -1:
            phone = phone.replace("Phone:", "").strip()
        ll = "".join(tree.xpath('//iframe[contains(@src, "maps")]/@src'))
        lll = "".join(
            tree.xpath(
                '//div[@class="sqs-block map-block sqs-block-map sized vsize-12"]/@data-block-json'
            )
        )

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if ll.find("embed") != -1:
            latitude = ll.split("!3d")[1].strip().split("!")[0].strip()
            longitude = ll.split("!2d")[1].strip().split("!")[0].strip()
        if lll.find("mapLat") != -1:
            latitude = lll.split('"mapLat":')[1].split(",")[0]
            longitude = lll.split('"mapLng":')[1].split(",")[0]

        country_code = "US"
        state = a.get("state")
        postal = a.get("ZipCode")
        city = a.get("city")
        store_number = "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//p[contains(text(), "HOURS")]/text() | //p[contains(text(), "Hours")]//text() | //p[contains(text(), "Mon")]//text() | //p/strong[contains(text(), "Open")]/text() | //p/strong[contains(text(), "MON")]/text()'
                )
            )
            .replace("Open for Dine-In!", "")
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            hours_of_operation.replace("Hours:", "")
            .replace("HOURS:", "")
            .replace("Open", "")
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
