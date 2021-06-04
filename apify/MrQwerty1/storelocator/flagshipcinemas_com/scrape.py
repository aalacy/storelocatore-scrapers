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


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_urls():
    urls = []
    session = SgRequests()
    r = session.get("https://flagshipcinemas.com/")
    tree = html.fromstring(r.text)
    links = tree.xpath("//h2[text()='Locations']/following-sibling::div//li")
    for li in links:
        link = "".join(li.xpath(".//a/@href"))
        text = "".join(li.xpath(".//a//text()"))
        if "Temporarily" in text:
            isclosed = True
        else:
            isclosed = False

        urls.append((link, isclosed))

    return urls


def get_data(url):
    isclosed = url[1]
    url = url[0]
    locator_domain = "https://flagshipcinemas.com/"
    page_url = f"https://flagshipcinemas.com{url}/page/contact"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    line = tree.xpath("//div[@class='mx-auto mb-8'][1]//text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1])
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"

    location_name = f"Flagship Cinemas {city}"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//div[contains(text(), 'Box Office')]//text()"))
        .split(":")[-1]
        .strip()
        or "<MISSING>"
    )
    text = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)
    location_type = "<MISSING>"
    hours_of_operation = "<MISSING>"

    if isclosed:
        hours_of_operation = "Temporarily Closed"

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
