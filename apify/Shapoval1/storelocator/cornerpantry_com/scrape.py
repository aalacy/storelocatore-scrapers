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
    locator_domain = "https://cornerpantry.com"
    api_url = "https://cornerpantry.com/store-locations/"
    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    page_urls = tree.xpath('//p[contains(text(), "We")]/a/@href')
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
        i = f"https://cornerpantry.com{i}"
        subr = session.get(i, headers=headers)
        trees = html.fromstring(subr.text)
        block = trees.xpath("//div[@class='entry-content']/h3[not(./a)]")
        for b in block:

            location_name = "".join(b.xpath(".//text()"))
            ad = b.xpath(".//following::p[1]/text() | .//following::p[1]/span/text()")
            ad = list(filter(None, [a.strip() for a in ad]))

            address = "".join(ad[0])
            if "".join(ad).find("488") != -1:
                address = " ".join(ad[:2])
            if "".join(ad).find("1800") != -1:
                address = " ".join(ad[:2])
            a = usaddress.tag(address, tag_mapping=tag)[0]
            street_address = f"{a.get('address1')} {a.get('address2')}".replace(
                "None", ""
            ).strip()
            city = a.get("city")
            state = a.get("state")
            postal = a.get("postal")
            country_code = "US"
            ll = "".join(b.xpath(".//following::iframe[1]/@src"))
            try:
                ll = ll.split("sll=")[1].split("&")[0]
            except IndexError:
                ll = ll.split("!2d")[1].split("!2m")[0].replace("!3d", ",")
            latitude = ll.split(",")[0]
            if ll.find("-81.2471217") != -1:
                latitude = ll.split(",")[1]
            longitude = ll.split(",")[1]
            if ll.find("-81.2471217") != -1:
                longitude = ll.split(",")[0]
            store_number = "".join(
                b.xpath(
                    './/following::h4[1][contains(text(), "Store")]/text() | .//following::h4[1]/strong[contains(text(), "Store")]/text()'
                )
            )
            store_number = store_number.split("Store")[1].strip()
            page_url = i
            phone = "".join(ad[-1]).replace("\n", "").replace("\t", "").strip()
            if "".join(ad).find("344") != -1:
                phone = "".join(ad[-2]).replace("\n", "").replace("\t", "").strip()
            if "".join(ad).find("661") != -1:
                phone = "".join(ad[-2]).replace("\n", "").replace("\t", "").strip()
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
