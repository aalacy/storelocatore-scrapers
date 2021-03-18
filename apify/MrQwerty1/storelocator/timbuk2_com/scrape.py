import csv

from concurrent import futures
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
    r = session.get("https://www.timbuk2.com/pages/stores")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='store-locations__button button button--left']/@href")


def get_data(url):
    locator_domain = "https://www.timbuk2.com/"
    page_url = f"https://www.timbuk2.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = " ".join(
        tree.xpath(
            "//h2[@class='large-title']/text()|//h3[@class='store-details__subtitle']/text()"
        )
    ).strip()
    line = tree.xpath(
        "//h6[text()='Contact']/following-sibling::div[@class='store-detais__foot_note_body']/p/text()"
    )

    phone = line[-1]
    street_address = ", ".join(line[:-2]).strip()
    line = line[-2]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.replace(state, "").strip()
    country_code = "US"
    if len(postal) > 5:
        country_code = "CA"
    store_number = "<MISSING>"
    latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        ";".join(
            tree.xpath(
                "//h6[text()='Hours']/following-sibling::div[@class='store-detais__foot_note_body']/p/text()"
            )
        )
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

    return row


def fetch_data():
    out = []
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
