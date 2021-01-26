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
    r = session.get("https://www.peachwaveyogurt.com/locations/?q=&search=Search")
    tree = html.fromstring(r.text)

    return tree.xpath("//h2[@class='cms-loc-directory-part-name']/a/@href")


def get_data(page_url):
    locator_domain = "https://www.peachwaveyogurt.com/"
    isclosed = False

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "Peachwave"
    line = tree.xpath("//div[@class='address']/p//text()")
    line = list(filter(None, [l.strip() for l in line]))

    if len(line) == 1:
        isclosed = True
        street_address, city, state, postal = (
            "<MISSING>",
            "<MISSING>",
            "<MISSING>",
            "<MISSING>",
        )
    elif len(line) == 0:
        return
    else:
        street_address = line[0]
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = " ".join(line.split()[:-1])
        postal = line.split()[-1]
        if postal == "Cayman":
            return

    country_code = "US"
    store_number = "<MISSING>"
    phone = "".join(tree.xpath("//div[@class='phone']/p/text()")).strip() or "<MISSING>"

    text = "".join(
        tree.xpath("//script[contains(text(), 'var myLocationMarker')]/text()")
    )
    try:
        text = text.split("new google.maps.LatLng")[1].split(";")[0]
        latitude, longitude = eval(text)
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    li = tree.xpath("//div[@class='cms-loc-directory-hours']//li")
    for l in li:
        day = "".join(l.xpath("./span/text()")).strip()
        time = "".join(l.xpath("./text()")).strip()
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if isclosed:
        hours_of_operation = "Closed"

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
