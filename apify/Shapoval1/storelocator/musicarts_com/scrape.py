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

    locator_domain = "https://www.musicarts.com/"
    api_url = "https://stores.musicarts.com/browse/"
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
    div = tree.xpath('//a[@class="ga-link"]')

    for d in div:
        sub_page_url = "".join(d.xpath(".//@href"))
        session = SgRequests()
        r = session.get(sub_page_url, headers=headers)
        tree = html.fromstring(r.text)
        urls = tree.xpath('//a[@class="ga-link"]')
        for u in urls:

            sspage_url = "".join(u.xpath(".//@href"))
            session = SgRequests()
            r = session.get(sspage_url, headers=headers)
            tree = html.fromstring(r.text)
            sub_urls = tree.xpath('//a[@class="more-details ga-link"]')
            for s in sub_urls:
                page_url = "".join(s.xpath(".//@href"))
                session = SgRequests()
                r = session.get(page_url, headers=headers)
                tree = html.fromstring(r.text)

                location_name = "".join(
                    tree.xpath(
                        '//div[@class="location-card-content"]//span[@class="location-name"]/text()'
                    )
                )
                ad = (
                    " ".join(
                        tree.xpath(
                            '//div[@class="location-card-content"]//div[@class="address"]/div/text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
                a = usaddress.tag(ad, tag_mapping=tag)[0]
                location_type = "Store"
                street_address = f"{a.get('address1')} {a.get('address2')}".replace(
                    "None", ""
                ).strip()
                phone = (
                    "".join(
                        tree.xpath(
                            '//div[@class="location-card-content"]//a[@class="phone ga-link"]/text()'
                        )
                    )
                    or "<MISSING>"
                )
                state = a.get("state") or "<MISSING>"
                postal = a.get("postal") or "<MISSING>"
                city = a.get("city") or "<MISSING>"
                country_code = "US"
                store_number = "<MISSING>"
                hours_of_operation = tree.xpath(
                    '//div[@class="day-hour-row"]/span//text()'
                )
                hours_of_operation = list(
                    filter(None, [a.strip() for a in hours_of_operation])
                )
                hours_of_operation = " ".join(hours_of_operation)
                ll = "".join(
                    tree.xpath(
                        '//div[@class="location-card-content"]//a[@class="directions ga-link"]/@href'
                    )
                )
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                if ll:
                    try:
                        latitude = ll.split("=")[-1].split(",")[0].strip()
                        longitude = ll.split("=")[-1].split(",")[1].strip()
                    except:
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"

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
