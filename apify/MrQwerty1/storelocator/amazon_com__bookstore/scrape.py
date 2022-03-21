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


def get_address(line):
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

    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
    if street_address == "None":
        street_address = "<MISSING>"
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    postal = a.get("postal") or "<MISSING>"

    return street_address, city, state, postal


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(
        "https://www.amazon.com/b/ref=s9_acss_bw_cg_A4S_1a1_w?node=17608448011&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-1&pf_rd_r=WK19DXM9JFEZAMXHPZ3Q&pf_rd_t=101&pf_rd_p=42158aca-d424-474e-a99c-843c73598ba7&pf_rd_i=17988552011#Amazon4starLocations",
        headers=headers,
    )
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//div[@class='a-row' and .//h2[text()='AMAZON BOOKS']]/following-sibling::div[1]//h3/following-sibling::p/a/@href"
    )


def fetch_data():
    out = []
    locator_domain = "https://amazon.com/bookstore"
    urls = get_urls()
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }

    for url in urls:
        page_url = f"https://www.amazon.com{url}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(
            tree.xpath(
                "//div[@class='bxc-grid__column  bxc-grid__column--6-of-12   bxc-grid__column--light']//h2//text()"
            )
        ).strip()

        if not location_name:
            urls.append(url)
            continue

        line = (
            "".join(
                tree.xpath(
                    "//p[./strong[contains(text(), 'Address')]]/a/text()|//p[./strong[contains(text(), 'Address')]]/text()"
                )
            )
            .replace(":", "")
            .replace("\n", " ")
            .strip()
        )
        street_address, city, state, postal = get_address(line)
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(tree.xpath("//p[./strong[contains(text(), 'Phone')]]/text()"))
            .replace(":", "")
            .strip()
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = (
                "".join(
                    tree.xpath(
                        "//p[./strong[contains(text(), 'Phone')]]/following-sibling::p[not(./strong)][1]/text()"
                    )
                )
                .replace(":", "")
                .strip()
                or "<MISSING>"
            )
        text = "".join(tree.xpath("//p[./strong[contains(text(), 'Address')]]/a/@href"))
        latitude, longitude = get_coords_from_google_url(text)
        location_type = "<MISSING>"

        _tmp = []
        hours = tree.xpath(
            "//p[./strong[contains(text(), 'Hours')]]/following-sibling::p[not(./strong)]/text()"
        )
        hours = list(filter(None, [h.strip() for h in hours]))
        for h in hours:
            if "Jan" in h:
                continue
            _tmp.append(h)
            if "Sat" in h and "Mon" not in h:
                break
        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        if "com" in phone:
            phone = "<MISSING>"
            hours_of_operation = "Coming Soon"

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
