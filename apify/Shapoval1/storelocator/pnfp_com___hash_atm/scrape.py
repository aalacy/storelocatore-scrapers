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

    locator_domain = "https://www.pnfp.com/"
    page_url = "https://www.pnfp.com/contact-us/pinnacle-locations-atms/all-locations/"
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Referer": "https://www.pnfp.com/contact-us/pinnacle-locations-atms/",
        "Upgrade-Insecure-Requests": "1",
        "TE": "Trailers",
    }

    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    size_pag = tree.xpath('//a[@class="btn btn-default"]/@href')
    first = "/contact-us/pinnacle-locations-atms/all-locations/?page=1"
    size_pag.insert(0, first)
    for slug in size_pag:
        page_url = f"https://www.pnfp.com{slug}"

        session = SgRequests()

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="location-item"]')
        for d in div:

            location_name = "".join(d.xpath(".//h2/text()")).replace("\n", "").strip()
            ad = d.xpath('.//div[@class="loc-col1"]/p/text()')
            ad = list(filter(None, [a.strip() for a in ad]))
            adr = " ".join(ad[:-1])
            if len(ad) < 3:
                adr = " ".join(ad)
            a = usaddress.tag(adr, tag_mapping=tag)[0]
            location_type = "Branch and ATM"
            street_address = f"{a.get('address1')} {a.get('address2')}".replace(
                "None", ""
            ).strip()
            state = a.get("state") or "<MISSING>"
            postal = a.get("postal") or "<MISSING>"
            country_code = "US"
            city = a.get("city") or "<MISSING>"
            if street_address.find("Oak Ridge") != -1:
                street_address = street_address.replace("Oak Ridge", "").strip()
                city = "Oak Ridge"
            if street_address.find("Knoxville") != -1:
                street_address = street_address.replace("Knoxville", "").strip()
                city = "Knoxville"
            store_number = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            phone = "".join(ad[-1])
            if len(ad) < 3:
                phone = "<MISSING>"
            hours_of_operation = (
                " ".join(
                    d.xpath('.//strong[text()="Lobby Hours"]/following-sibling::text()')
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )

            if hours_of_operation.find("The lobby") != -1:
                hours_of_operation = hours_of_operation.split("The lobby")[0].strip()
            if "office" in hours_of_operation:
                location_type = "Office"
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
