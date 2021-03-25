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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

    r = session.get("https://kruseandmuerrestaurants.com/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//div[@class='fl-photo-content fl-photo-img-png']/a[contains(@href, 'location')]/@href"
    )


def get_data(page_url):
    locator_domain = "https://kruseandmuerrestaurants.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = tree.xpath("//h2[@class='fl-heading']/span/text()")[0].strip()
    line = tree.xpath("////p[@class='lead']/preceding-sibling::address//text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1]).strip()
    line = line[-1].replace(",", "")
    postal = line.split()[-1]
    state = line.split()[-2]
    city = line.split(state)[0].strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = "".join(tree.xpath("//p[@class='lead']/a/text()")).strip() or "<MISSING>"

    text = "".join(tree.xpath("//a[@class='map-btn']/@href"))
    latitude, longitude = get_coords_from_google_url(text)
    location_type = "<MISSING>"

    _tmp = []
    tr = tree.xpath("//tr[@class='tbody-row']")

    for t in tr:
        day = "".join(t.xpath("./td[1]//text()")).strip()
        time = "".join(t.xpath("./td[2]//text()")).strip()
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
