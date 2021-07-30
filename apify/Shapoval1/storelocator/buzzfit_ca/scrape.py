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

    locator_domain = "https://www.buzzfit.ca"

    api_url = "https://www.buzzfit.ca/find-a-gym/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath('//a[@class="button button--yellow"]')
    for b in block:
        slug = "".join(b.xpath(".//@href"))
        page_url = f"{locator_domain}{slug}"
        phone = "<MISSING>"
        if page_url.find("/buzzfit-chateauguay") != -1:
            phone = (
                "".join(b.xpath(".//preceding-sibling::span//text()"))
                .replace("Phone:", "")
                .strip()
            )

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/text()"))
        location_type = "<MISSING>"
        street_address = "".join(
            tree.xpath("//div[contains(@class, 'address')]/p[1]/text()[1]")
        )
        adr = (
            "".join(tree.xpath("//div[contains(@class, 'address')]/p[1]/text()[2]"))
            .replace("\n", "")
            .replace(", QC", "")
            .replace("H1G5X5", "H1G 5X5")
            .replace("J6W3Z5", "J6W 3Z5")
            .strip()
        )
        country_code = "Canada"

        if page_url.find("/buzzfit-chateauguay") == -1:
            phone = (
                "".join(tree.xpath("//div[contains(@class, 'address')]/p[1]/text()[3]"))
                .replace("\n", "")
                .strip()
            )

        state = "Quebec"
        postal = " ".join(adr.split()[-2:])
        city = " ".join(adr.split()[0:-2]).strip()
        store_number = "<MISSING>"
        hours_of_operation = tree.xpath(
            "//div[contains(@class, 'address')]/p[2]//text()"
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = (
            " ".join(hours_of_operation)
            .replace("Open and Staffed from", "")
            .replace("a day", "")
            .replace("7 days a week!", "")
            .replace(",", "")
            .strip()
        )
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
