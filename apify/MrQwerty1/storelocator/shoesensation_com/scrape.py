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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "text/html, */*; q=0.01",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.shoesensation.com",
        "Connection": "keep-alive",
        "Referer": "https://www.shoesensation.com/store-locator",
        "TE": "Trailers",
    }

    r = session.post(
        "https://www.shoesensation.com/store_locator/location/updatemainpage",
        headers=headers,
    )
    tree = html.fromstring(r.text)

    return tree.xpath("//div[contains(text(), 'Details')]/@data-href")


def get_data(page_url):
    locator_domain = "https://www.shoesensation.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//h2[@class='mw-sl__details__name']/text()")
    ).strip()
    line = tree.xpath(
        "//li[@class='mw-sl__details__item mw-sl__details__item--location']/div[@class='info']/text()"
    )
    line = list(
        filter(None, [" ".join(l.replace("United States", "").split()) for l in line])
    )

    street_address = line[0].rsplit(",", 1)[0].strip()
    city = line[0].rsplit(",", 1)[1].strip()
    state = line[1].split(",")[0].strip()
    postal = line[1].split(",")[1].strip()

    if f", {city}" in street_address:
        street_address = street_address.split(f", {city}")[0].strip()
    country_code = "US"
    store_number = page_url.split("-")[-1]
    if store_number.isalpha():
        store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//a[@class='btn btn-link phone']/text()")).strip()
        or "<MISSING>"
    )
    text = "".join(tree.xpath("//iframe/@src"))
    try:
        latitude, longitude = text.split("&center=")[1].split(",")
        if "0.00" in latitude:
            raise IndexError
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    divs = tree.xpath("//div[@class='mw-sl__infotable__row']")
    for d in divs:
        day = "".join(d.xpath("./span[1]/text()")).replace("|", "").strip()
        time = "".join(d.xpath("./span[2]/text()")).strip()
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

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
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
