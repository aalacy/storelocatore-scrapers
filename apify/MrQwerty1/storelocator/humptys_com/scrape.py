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


def get_urls():
    session = SgRequests()
    r = session.get("https://www.humptys.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//li[./a[contains(text(), 'COVID-19 hours')]]/following-sibling::li/a/@href"
    )


def fetch_data():
    out = []
    session = SgRequests()
    locator_domain = "https://www.humptys.com/"
    location_name = "Humpty's Restaurant"
    postal = "<MISSING>"
    country_code = "CA"
    store_number = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = "<MISSING>"

    urls = get_urls()
    for page_url in urls:
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        state = "".join(
            tree.xpath("//li[contains(@class,'current_page_item')]/a/text()")
        ).strip()
        cities = tree.xpath("//h3[./strong]|//h3")

        for c in cities:
            city = "".join(c.xpath("./strong/text()|./text()")).strip()
            tr = c.xpath("./following-sibling::table[1]//tr[./td]")
            for t in tr:
                street_address = "".join(t.xpath("./td[1]/text()")).strip()
                phone = "".join(t.xpath("./td[2]/text()")).strip()

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
