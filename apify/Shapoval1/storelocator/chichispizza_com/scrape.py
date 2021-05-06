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

    locator_domain = "https://www.chichispizza.com"
    api_url = "https://www.chichispizza.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./h2]")
    cov = "".join(tree.xpath('//span[contains(text(), "COVID")]/text()'))
    for d in div:
        page_url = "https://www.chichispizza.com/locations"
        location_name = "".join(d.xpath(".//text()")).replace("\n", "").strip()
        location_type = "<MISSING>"

        street_address = "".join(d.xpath(".//following-sibling::div[1]/p[1]/text()"))
        ad = "".join(d.xpath(".//following-sibling::div[1]/p[2]/text()"))
        if street_address.find("(") != -1:
            street_address = "".join(
                d.xpath(".//following-sibling::div[1]/p[2]/text()")
            )
            ad = "".join(d.xpath(".//following-sibling::div[1]/p[3]/text()"))
        phone = "".join(
            d.xpath('.//following-sibling::div[1]//a[contains(@href, "tel")]//text()')
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/following::p[./span[text()="HOURS"]]/following-sibling::p[position()>1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if cov:
            session = SgRequests()
            r = session.get("https://www.chichispizza.com/", headers=headers)
            tree = html.fromstring(r.text)
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//p[.//span[contains(text(), "Temporary")]]/following-sibling::p[1]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
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
