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
    locator_domain = "https://www.yogapod.com"
    api_url = "https://www.yogapod.com/"
    session = SgRequests()
    r = session.get(api_url)
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

    div = tree.xpath('//div[@class=" vc_custom_1601583357342"]/div/div/select/option')
    for d in div:

        slug = "".join(d.xpath(".//@value"))
        if slug == "":
            continue
        if slug.find("/apex/") != -1:
            slug = "/apexgainesvillenw/"
        page_url = f"{locator_domain}{slug}"
        if page_url.find("https://www.yogapod.com/gainesvillesw/") != -1:
            continue
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        div = tree.xpath('//ul[@itemscope="itemscope"]')
        for d in div:
            line = d.xpath('.//span[@itemprop="address"]//text()')
            line = list(filter(None, [a.strip() for a in line]))
            line = " ".join(line)
            ad = line
            if line.find("University") != -1:
                line = line.split("Center")[1].strip()
            if line.find("Plaza") != -1:
                line = line.split("Plaza")[1].strip()
            a = usaddress.tag(line, tag_mapping=tag)[0]
            street_address = f"{a.get('address1')} {a.get('address2')}".replace(
                "None", ""
            ).strip()
            if street_address.find("3045") != -1:
                street_address = " ".join(ad.split(",")[:2]).replace("  ", " ").strip()
            if street_address.find("4280") != -1:
                street_address = ad.split("Tucson")[0].replace(",", "")
            city = a.get("city")
            state = a.get("state")
            postal = a.get("postal")
            country_code = "US"
            store_number = "<MISSING>"
            location_name = "".join(d.xpath('.//span[@itemprop="jobTitle"]/text()'))
            phone = "".join(
                d.xpath(
                    './/*[contains(@data-name, "mk-icon-phone")]/following-sibling::span/text()'
                )
            )
            map_link = "".join(
                d.xpath('.//preceding::iframe[contains(@src, "/maps/embed")]/@src')
            )

            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
            if street_address.find("3045") != -1:
                map_link = "".join(
                    d.xpath('.//preceding::iframe[contains(@src, "-82.37053")]/@src')
                )
                latitude = map_link.split("!1d")[1].strip().split("!")[0].strip()
                longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
            location_type = "<MISSING>"
            hours_of_operation = (
                " ".join(
                    d.xpath(
                        './/preceding::h4[contains(text(), "HOURS")]/following-sibling::h6/text()'
                    )
                )
                .replace("\n", "")
                .replace("Child Care 8:00AM – 10:30AM", "")
                .strip()
                or "<MISSING>"
            )
            if page_url.find("gainesville") != -1:
                page_url = "https://www.yogapod.com/gainesville/"

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
