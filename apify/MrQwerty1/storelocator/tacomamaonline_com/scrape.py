import csv
import re

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


def clean_phone(text):
    out = []

    for t in text:
        if t.isdigit():
            out.append(t)
        if len(out) == 10:
            break

    return "(" + "".join(out[:3]) + ") " + "".join(out[3:6]) + "-" + "".join(out[6:])


def get_urls():
    session = SgRequests()
    r = session.get("https://tacomamaonline.com/locations-menus/")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[contains(@class,'location-box ')]//a/@href")


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_data(page_url):
    locator_domain = "https://tacomamaonline.com/"
    location_type = "<MISSING>"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//title/text()")).replace("-", "").strip()
    line = tree.xpath("//div[@class='address_info']/p/text()")
    line = list(filter(None, [l.strip() for l in line]))
    index = 0
    for li in line:
        if re.findall(r"\d{5}", li):
            break
        index += 1

    street_address = " ".join(line[:index]).strip() or "<MISSING>"
    csz = line[index]
    line = line[index + 1 :]
    city = csz.split(",")[0].strip()
    csz = csz.split(",")[1].strip()
    state = csz.split()[0]
    postal = csz.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    text = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)
    phone = "<MISSING>"
    for li in line:
        if re.findall(r"\d{3}-\d{3}", li):
            phone = clean_phone(line.pop(line.index(li)))
            break

    hours_of_operation = " ".join(line).replace("–", "-") or "<MISSING>"

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
