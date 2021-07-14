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

    locator_domain = "https://www.sugarmountain.ca/"
    page_url = "https://www.sugarmountain.ca/contacts.html"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    div = tree.xpath("//article[contains(@id, 'item')]")

    for d in div:

        location_name = (
            " ".join(
                d.xpath('.//h2[@class="item_title item_title__home_menu"]/span/text()')
            )
            .replace("\n", "")
            .strip()
        )
        address = (
            "".join(
                d.xpath(
                    './/preceding::script[contains(text(), "var markers404 = ")]/text()'
                )
            )
            .split("var markers404 = ")[1]
            .split(f"{location_name}")[1]
            .split(";")[0]
            .split('","')[2]
            .split('"]')[0]
            .strip()
        )
        address = (
            address.replace("(Across from Apple)", "")
            .replace("  ", " ")
            .replace("ON,", "ON")
            .replace("Orléans", ",Orléans")
        )
        location_type = "<MISSING>"
        street_address = address.split(",")[0].strip()
        state = address.split(",")[2].split()[0].strip()
        postal = " ".join(address.split(",")[2].split()[1:])
        country_code = "CA"
        city = address.split(",")[1].strip()
        store_number = "<MISSING>"
        ll = (
            "".join(
                d.xpath(
                    './/preceding::script[contains(text(), "var markers404 = ")]/text()'
                )
            )
            .split("var markers404 = ")[1]
            .split(f"{location_name}")[0]
            .split(";")[0]
        )
        latitude = ll.split(",")[-3]
        longitude = ll.split(",")[-2]
        phone = (
            "".join(d.xpath(".//h4/following-sibling::p[1]/text()[3]"))
            .replace("Tel:", "")
            .strip()
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = (
                "".join(d.xpath(".//h4/following-sibling::p[1]/text()[2]"))
                .replace("Tel:", "")
                .strip()
                or "<MISSING>"
            )
        hours_of_operation = (
            " ".join(d.xpath(".//table//tr/td/text()")).replace("\n", "").strip()
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
