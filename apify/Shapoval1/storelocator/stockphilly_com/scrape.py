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

    locator_domain = "https://www.stockphilly.com/"
    api_url = "https://www.stockphilly.com/nav-modal"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[contains(@id, "stock-menu-modal-hours")]//div[contains(@class, "stock-modal-hours-container")]'
    )
    for d in div:
        page_url = "https://www.stockphilly.com/"
        location_name = "<MISSING>"
        location_type = "<MISSING>"
        street_address = "<MISSING>"
        phone = "".join(
            d.xpath(
                './/following::div[contains(@class, "stock-modal-menu-disclaimer")]/text()'
            )
        )
        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "US"
        city = "<MISSING>"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = (
            " ".join(d.xpath(".//div/text()")).replace("\n", "").strip()
        )

        if hours_of_operation.find("Mon") == -1:
            phone = phone.split("\n")[0].replace("Walk-in only,", "").strip()
            street_address = (
                "".join(
                    d.xpath(
                        './/following::div[contains(@class, "Fishtown stock-menu-modal-address-item")]/text()'
                    )
                )
                .split("\n")[0]
                .replace("\n", "")
                .strip()
            )
            city = (
                "".join(
                    d.xpath(
                        './/following::div[contains(@class, "Fishtown stock-menu-modal-address-item")]/text()'
                    )
                )
                .split("\n")[1]
                .split(",")[0]
                .strip()
            )
            state = (
                "".join(
                    d.xpath(
                        './/following::div[contains(@class, "Fishtown stock-menu-modal-address-item")]/text()'
                    )
                )
                .split("\n")[1]
                .split(",")[1]
                .split()[0]
                .strip()
            )
            postal = (
                "".join(
                    d.xpath(
                        './/following::div[contains(@class, "Fishtown stock-menu-modal-address-item")]/text()'
                    )
                )
                .split("\n")[1]
                .split(",")[1]
                .split()[1]
                .strip()
            )
            location_name = "Fishtown"
        if hours_of_operation.find("Mon") != -1:
            phone = phone.split("\n")[1].strip()
            street_address = (
                "".join(
                    d.xpath(
                        './/following::div[contains(@class, "Rittenhouse stock-menu-modal-address-item")]/text()'
                    )
                )
                .split("\n")[0]
                .replace("\n", "")
                .strip()
            )
            city = (
                "".join(
                    d.xpath(
                        './/following::div[contains(@class, "Rittenhouse stock-menu-modal-address-item")]/text()'
                    )
                )
                .split("\n")[1]
                .split(",")[0]
                .strip()
            )
            state = (
                "".join(
                    d.xpath(
                        './/following::div[contains(@class, "Rittenhouse stock-menu-modal-address-item")]/text()'
                    )
                )
                .split("\n")[1]
                .split(",")[1]
                .split()[0]
                .strip()
            )
            postal = (
                "".join(
                    d.xpath(
                        './/following::div[contains(@class, "Rittenhouse stock-menu-modal-address-item")]/text()'
                    )
                )
                .split("\n")[1]
                .split(",")[1]
                .split()[1]
                .strip()
            )
            location_name = "Rittenhouse"
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
