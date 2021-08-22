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

    locator_domain = "https://www.albiernats.com/"
    api_url = "https://www.albiernats.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[./p[contains(text(), "Al Biernat")]]')

    for d in div:
        location_name = "".join(d.xpath(".//p/text()"))

        page_url = "".join(d.xpath(".//@href"))
        if page_url.find("http") == -1:
            page_url = "https://www.albiernats.com/contact.html"
        if page_url.find("/contact.html") == -1:
            page_url = page_url + "/contact.html"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ad = (
            "".join(
                tree.xpath(
                    '//div[./*[text()="address"]]/following-sibling::div[1]//text() | //div[./*[text()="Address"]]/following-sibling::div[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )

        location_type = "<MISSING>"
        street_address = ad.split(",")[0].strip()
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]//text()'))
        state = ad.split(",")[2].split()[0].strip()
        postal = ad.split(",")[2].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[1].strip()
        store_number = "<MISSING>"
        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        hours_of_operation = (
            " ".join(tree.xpath('//div[./p[contains(text(), "am")]]/p//text()'))
            .replace("\n", "")
            .replace("   ", " ")
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
