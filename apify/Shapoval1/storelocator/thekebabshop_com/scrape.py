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
    locator_domain = "https://www.thekebabshop.com"
    api_url = "https://www.thekebabshop.com"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    page_urls = set(tree.xpath('////nav[@class="header-nav-list"]/div[1]/div//a/@href'))
    for i in page_urls:
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
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Referer": "https://www.thekebabshop.com/losangeles",
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }
        i = f"https://www.thekebabshop.com{i}"
        subr = session.get(i, headers=headers)
        trees = html.fromstring(subr.text)
        block = trees.xpath("//div[./h2]")

        for b in block:
            location_name = "".join(b.xpath(".//h2/text() | .//h2/strong/text()"))

            ad = " ".join(b.xpath(".//p/a[1]/text()"))
            if location_name.find("HARVARD") != -1:
                ad = (
                    " ".join(b.xpath('.//p[./a[contains(text(), "17655")]]//text()'))
                    .split("949")[0]
                    .replace("I rvine", "Irvine")
                    .strip()
                )
            if ad == "":
                continue
            a = usaddress.tag(ad, tag_mapping=tag)[0]
            street_address = f"{a.get('address1')} {a.get('address2')}".replace(
                "None", ""
            ).strip()
            city = a.get("city")
            if street_address.find("127") != -1:
                street_address = ad.split("  ")[0]
                city = ad.split("  ")[1].split(",")[0]
            state = a.get("state")
            postal = a.get("postal")
            country_code = "US"

            store_number = "<MISSING>"
            page_url = i

            phone = "".join(
                b.xpath('.//p/text() | .//a[contains(@href, "tel")]/text()')
            )
            if phone.find("I") != -1:
                phone = phone.replace("I", "")
            if phone.find("(NOW OPEN)") != -1:
                phone = phone.replace("(NOW OPEN)", "")
            if phone.find("Early") != -1:
                phone = "<MISSING>"
            text = "".join(b.xpath(".//a[contains(@href, 'google')]/@href"))
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
