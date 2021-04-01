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
    r = session.get("https://fixauto.com/ca-qc/en/all-shops?worldwide=yes")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//div[./div[contains(text(),'United States') or contains(text(), 'Canada') or contains(text(), 'United Kingdom')]]/a/@href"
    )


def get_data(page_url):
    locator_domain = "https://fixauto.com/"
    session = SgRequests()
    r = session.get(page_url)
    if r.status_code != 200:
        return
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//div[@id='shopname']/text()")).strip()
    line = tree.xpath("//div[@class='address-col1']/text()")
    line = list(filter(None, [l.strip() for l in line]))
    line = line[1:]
    if line:
        street_address = " ".join(line[0].split()).strip()
        postal = line[-1].strip()
        line = line[1].strip()
        city = line.split(",")[0].strip()
        try:
            state = line.split(",")[1].strip()
        except IndexError:
            state = "<MISSING>"

        if not city:
            city = (
                "".join(tree.xpath("//div[@class='address-col1']/b/text()")).strip()
                or "<MISSING>"
            )
        elif city[0].isdigit():
            city = "<MISSING>"
            state = line.split(",")[-1].strip()

        if street_address == "23765 SE 264th St.":
            city = "Maple Valley"
            state = "Washington"
            postal = "98038"

        country = "".join(
            tree.xpath("//font[@style=' text-transform:uppercase;']/text()")
        ).strip()
        if country == "canada":
            country_code = "CA"
        elif country == "uk":
            country_code = "GB"
        else:
            country_code = "US"

    else:
        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "<MISSING>"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//div[@class='address-col2']/text()")).strip()
        or "<MISSING>"
    )

    script = "".join(
        tree.xpath("//script[contains(text(), 'new google.maps.LatLng')]/text()")
    )
    try:
        latitude = script.split("LatLng(")[1].split(",")[0]
        longitude = script.split("LatLng(")[1].split(",")[1].split(")")[0]
    except IndexError:
        latitude = "<MISSING>"
        longitude = "<MISSING>"

    location_type = "<MISSING>"

    _tmp = []
    divs = tree.xpath(
        "//div[@style='display: flex; padding: 8px 0; border-bottom: 1px solid #888;']"
    )
    for d in divs:
        day = "".join(d.xpath("./div[1]//text()")).strip()
        time = " ".join("".join(d.xpath("./div[2]//text()")).split())
        _tmp.append(f"{day} {time}")

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
