import csv
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

    locator_domain = "https://www.bankatfidelity.com"
    api_url = "https://www.bankatfidelity.com/about/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="mod-branch-list"]')

    for d in div:
        location_name = "".join(d.xpath('.//div[@class="address"]/h3/text()'))
        if location_name.find("ATM") != -1:
            continue
        page_url = locator_domain + "".join(
            d.xpath('.//a[contains(text(), "View Details")]/@href')
        )
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_type = "Bank"
        street_address = "".join(tree.xpath('//li[@class="address"]/text()[1]'))
        ad = (
            "".join(tree.xpath('//li[@class="address"]/text()[2]'))
            .replace("\n", "")
            .strip()
        )
        phone = "".join(tree.xpath('//span[@class="phone"]/text()')) or "<MISSING>"
        state = ad.split(",")[1].split()[0].strip() or "<MISSING>"
        postal = ad.split(",")[1].split()[1].strip() or "<MISSING>"
        country_code = "US"
        city = ad.split(",")[0].strip() or "<MISSING>"
        store_number = "<MISSING>"
        latitude = (
            "".join(tree.xpath('//img[@class="branch_map"]/@src'))
            .split("center=")[1]
            .split(",")[0]
            .strip()
        )
        if not latitude.startswith("41") and not latitude.startswith("40"):
            latitude = "<MISSING>"
        longitude = (
            "".join(tree.xpath('//img[@class="branch_map"]/@src'))
            .split("center=")[1]
            .split(",")[1]
            .split("&")[0]
            .strip()
        )
        if not longitude.startswith("-76") and not longitude.startswith("-75"):
            longitude = "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[./h3[contains(text(), "Lobby Hours")]]/following-sibling::div/dl//text() | //div[./h3[contains(text(), "Lobby hours")]]/following-sibling::div/dl//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//div[./h3[contains(text(), "Office hours")]]/following-sibling::div/dl//text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
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
