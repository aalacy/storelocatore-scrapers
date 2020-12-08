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


def get_ids():
    ids = []
    session = SgRequests()
    r = session.get(
        "https://www.itsfashions.com/location.aspx?stores=both&radius=999999999&zip=75022"
    )
    tree = html.fromstring(r.text)
    links = tree.xpath("//div[@class='location']//a/@href")
    for l in links:
        ids.append(l.split("=")[-1])

    return ids


def get_data(_id):
    locator_domain = "https://itsfashions.com/"
    page_url = f"https://www.itsfashions.com/location.aspx?id={_id}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h3[@class='cityheader']/text()")).strip()
    line = tree.xpath("//div[@class='location']/div[not(@class) and not(@id)]/text()")
    line = list(filter(None, [l.strip() for l in line]))

    # city, state, postal index
    i = 0
    street_address = "<MISSING>"
    for l in line:
        if l[0].strip().isdigit():
            street_address = l
        if l.find("\r\n") != -1:
            break
        i += 1

    part_line = line[i]

    city = part_line.split("\r\n")[0][:-1].strip()
    state = part_line.split("\r\n")[1].strip()
    postal = part_line.split("\r\n")[-1].strip()

    try:
        phone = line[i + 1]
    except IndexError:
        phone = "<MISSING>"

    country_code = "US"
    store_number = _id
    latitude = (
        "".join(
            tree.xpath(
                "//input[@id='ContentPlaceHolder1_locations1_HiddenFieldLat']/@value"
            )
        )
        or "<MISSING>"
    )
    longitude = (
        "".join(
            tree.xpath(
                "//input[@id='ContentPlaceHolder1_locations1_HiddenFieldLng']/@value"
            )
        )
        or "<MISSING>"
    )
    location_type = (
        "".join(tree.xpath("//div[@class='store']/text()")).replace("It's ", "").strip()
    )
    hours_of_operation = "<MISSING>"

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
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, _id): _id for _id in ids}
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
