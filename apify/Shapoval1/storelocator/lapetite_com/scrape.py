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

    locator_domain = "https://www.chusmart.com"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(
        "https://www.lapetite.com/child-care-centers/find-a-school/", headers=headers
    )
    tree = html.fromstring(r.text)
    div = tree.xpath("//map/area")

    for d in div:

        slug = "".join(d.xpath(".//@href"))
        pages_url = f"https://www.lapetite.com{slug}"
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
        r = session.get(pages_url, headers=headers)
        tree = html.fromstring(r.text)
        urls = tree.xpath('//div[@class="locationCard"]')
        for url in urls:

            page_url = "".join(url.xpath('.//a[@class="schoolNameLink"]/@href'))
            if page_url.find("https:") != -1:
                continue
            if page_url.find("https:") == -1:
                page_url = f"https://www.lapetite.com{page_url}"
            latitude = "".join(
                url.xpath('.//a[@class="addrLink addrLinkToMap"]//@data-latitude')
            )
            longitude = "".join(
                url.xpath('.//a[@class="addrLink addrLinkToMap"]//@data-longitude')
            )
            ad = (
                "".join(
                    url.xpath(
                        './/a[@class="addrLink addrLinkToMap"]//span[@class="addr"]/span/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            a = usaddress.tag(ad, tag_mapping=tag)[0]
            location_name = (
                "".join(url.xpath('.//div[@class="cardBtm"]//h2//text()'))
                .replace("\n", "")
                .strip()
            )
            street_address = (
                f"{a.get('address1')} {a.get('address2')}".replace("None", "").strip()
                or "<MISSING>"
            )
            phone = (
                "".join(url.xpath('.//p[@class="phone vcard"]/a//text()'))
                or "<MISSING>"
            )
            state = a.get("state") or "<MISSING>"
            postal = a.get("postal") or "<MISSING>"
            country_code = "US"
            city = a.get("city") or "<MISSING>"
            store_number = "".join(url.xpath(".//@data-school-id")) or "<MISSING>"
            hours_of_operation = (
                "".join(url.xpath('.//p[@class="hours"]/text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            location_type = "La Petite Academy"

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

    locator_domain = "https://www.lapetite.com/"
    api_url = "https://www.lapetite.com/child-care-centers/find-a-school/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//map/area")
    for d in div:
        slug = "".join(d.xpath(".//@href")).split("=")[-1].strip()
        session = SgRequests()
        r = session.get(
            f"https://www.lapetite.com/locations/search-results-other-brands-paged-json/?location={slug}&range=40&skip=0&top=1000",
            headers=headers,
        )
        js = r.json()["Items"]
        for j in js:

            page_url = j.get("SchoolUrl") or "<MISSING>"
            location_name = j.get("SchoolName") or "<MISSING>"
            location_type = j.get("BrandName") or "<MISSING>"
            street_address = (
                f"{j.get('Address1')} {j.get('Address2')}".strip() or "<MISSING>"
            )
            phone = j.get("PhoneNumber") or "<MISSING>"
            if phone == "0000000000":
                phone = "<MISSING>"
            state = j.get("State") or "<MISSING>"
            postal = j.get("ZipCode") or "<MISSING>"
            country_code = "US"
            city = j.get("City") or "<MISSING>"
            store_number = j.get("SchoolId") or "<MISSING>"
            latitude = j.get("Latitude") or "<MISSING>"
            longitude = j.get("Longitude") or "<MISSING>"
            hours_of_operation = j.get("HoursOfOperation") or "<MISSING>"

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

    locator_domain = "https://www.lapetite.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    session = SgRequests()
    r = session.get(
        "https://www.lapetite.com/locations/search-results-other-brands-paged-json/?location=NY&range=40&skip=0&top=1000",
        headers=headers,
    )
    js = r.json()["Items"]
    for j in js:

        page_url = j.get("SchoolUrl") or "<MISSING>"
        location_name = j.get("SchoolName") or "<MISSING>"
        location_type = j.get("BrandName") or "<MISSING>"
        street_address = (
            f"{j.get('Address1')} {j.get('Address2')}".strip() or "<MISSING>"
        )
        phone = j.get("PhoneNumber") or "<MISSING>"
        if phone == "0000000000":
            phone = "<MISSING>"
        state = j.get("State") or "<MISSING>"
        postal = j.get("ZipCode") or "<MISSING>"
        country_code = "US"
        city = j.get("City") or "<MISSING>"
        store_number = j.get("SchoolId") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        hours_of_operation = j.get("HoursOfOperation") or "<MISSING>"

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
