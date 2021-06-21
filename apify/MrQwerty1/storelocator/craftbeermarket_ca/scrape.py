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
    r = session.get("https://www.craftbeermarket.ca/locations")
    tree = html.fromstring(r.text)

    return tree.xpath("//p/a[contains(text(), 'more info')]/@href")


def get_postal(text):
    try:
        postal = " ".join(text.split("/@")[0].split("+")[-2:])
        if len(postal) == 7:
            return postal
        else:
            return "<MISSING>"
    except IndexError:
        return "<MISSING>"


def get_data(page_url):
    locator_domain = "https://www.craftbeermarket.ca/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[@class='locationContactInfo']/h4/text()")
    ).strip()
    line = tree.xpath("//div[@class='locationContactInfo']/p/text()")
    line = "  ".join(list(filter(None, [l.strip() for l in line])))
    line = line.split("  ")
    phone = line.pop().strip()
    line = line[0].replace("KELOWNA", ",KELOWNA").split(",")

    state = line.pop().strip()
    city = line.pop().strip()
    if "BC" in city:
        state = "BC"
        city = city.replace("BC", "").strip()
    street_address = line[0]
    text = "".join(
        tree.xpath(
            "//a[@class='button _darkBrown' and contains(@href, 'google')]/@href"
        )
    )
    postal = get_postal(text)
    country_code = "CA"
    store_number = "<MISSING>"
    latitude = (
        "".join(tree.xpath("//div[@data-latitude]/@data-latitude")) or "<MISSING>"
    )
    longitude = (
        "".join(tree.xpath("//div[@data-longitude]/@data-longitude")) or "<MISSING>"
    )
    location_type = "<MISSING>"

    _tmp = []
    divs = tree.xpath("//h4[contains(text(), 'Hours')]/following-sibling::ul/li")
    for d in divs:
        day = "".join(d.xpath("./strong/text()")).strip()
        time = "".join(d.xpath("./text()")).strip()
        if not day or not time:
            continue
        if "takeout" in time.lower() or "pation" in time.lower():
            continue
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
