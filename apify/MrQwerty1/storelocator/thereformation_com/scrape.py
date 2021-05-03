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


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_urls():
    session = SgRequests()
    r = session.get("https://www.thereformation.com/pages/stores")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='image-new-content-block__content-link']/@href")


def get_data(page_url):
    locator_domain = "https://www.thereformation.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    lines = tree.xpath(
        "//div[@class='content-block content-block--hidden-for-small content-block--image-new content-block--show-divider-true']//text()"
    )
    lines = list(filter(None, [l.strip() for l in lines]))
    hours_index = 0
    for l in lines:
        if l.startswith("Hours:"):
            break
        hours_index += 1

    line = lines[1:hours_index]
    street_address = ", ".join(line[:-1]).replace(",,", ",")
    if "Mall" in street_address:
        street_address = street_address.split("Mall,")[1].strip()
    city = line[-1]
    state = "<MISSING>"
    postal = "<MISSING>"
    if city == "London":
        country_code = "GB"
    elif city == "North York":
        country_code = "CA"
    else:
        country_code = "US"
    store_number = "<MISSING>"
    try:
        phone = tree.xpath(
            "//div[@class='content-block content-block--hidden-for-small content-block--image-new content-block--show-divider-true']//a[contains(@href, 'tel:')]/@href"
        )[-1].replace("tel:+", "")
    except IndexError:
        phone = "<MISSING>"
    text = "".join(
        tree.xpath(
            "//div[@class='content-block content-block--hidden-for-small content-block--image-new content-block--show-divider-true']//a[contains(@href, 'google')]/@href"
        )
    )
    latitude, longitude = get_coords_from_google_url(text)
    location_type = "<MISSING>"
    hours_of_operation = (
        ";".join(lines[hours_index + 1 : lines.index("Call:")]) or "Closed"
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
