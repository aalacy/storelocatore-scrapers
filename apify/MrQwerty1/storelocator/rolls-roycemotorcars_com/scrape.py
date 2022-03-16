import csv

from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgpostal import International_Parser, parse_address


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
    r = session.get("https://www.rolls-roycemotorcars.com/en_GB/dealers/site-map.html")
    tree = html.fromstring(r.content)

    return tree.xpath(
        "//div[./div/div/h2[contains(text(),'United Kingdom') or contains(text(),'Americas')]]/following-sibling::div[1]//a/@href"
    )


def get_data(page_url):
    locator_domain = "https://www.rolls-roycemotorcars.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath(
        "//div[@class='rrmc-find-us-content--split js-rrmc-find-us-content--split ' and @data-index='0']//div[@class='rrmc-find-us--address']//text()"
    )
    line = " ".join(list(filter(None, [l.strip() for l in line])))
    if not line or line == "-":
        return

    adr = parse_address(International_Parser(), line)

    street_address = (
        f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
            "None", ""
        ).strip()
        or "<MISSING>"
    )
    city = adr.city or "<MISSING>"
    state = adr.state or "<MISSING>"
    postal = adr.postcode or "<MISSING>"
    country_code = adr.country or "<MISSING>"
    if "en_US" in page_url:
        country_code = "US"
    if "Scotland" in state or "United" in country_code:
        country_code = "GB"
    if city in ["Toronto", "Montreal", "Vancouver"]:
        country_code = "CA"

    if country_code not in ["US", "GB", "CA"]:
        return

    if street_address == "Unit 1":
        street_address = line.split("Unit 1")[0] + "Unit 1"

    if postal == "<MISSING>" and country_code == "GB":
        postal = " ".join(street_address.split()[-2:])
        street_address = street_address.replace(postal, "").strip()

    if street_address == "<MISSING>":
        street_address = line.split(postal)[0].replace(",", "").strip()
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//div[@class='rrmc-find-us-content--split js-rrmc-find-us-content--split ' and @data-index='0']//a[@data-channel='telephone']/span/text()"
            )
        ).strip()
        or "<MISSING>"
    )
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"

    hours = tree.xpath(
        "//div[@class='rrmc-find-us-content--split js-rrmc-find-us-content--split ' and @data-index='0']//div[@class='rrmc-find-us--opening-hours-entry']//text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = " ".join(";".join(hours).split()) or "<MISSING>"

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

    with futures.ThreadPoolExecutor(max_workers=2) as executor:
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
