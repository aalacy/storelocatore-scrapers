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
    session = SgRequests()
    r = session.get("https://www.paintingwithatwist.com/locations/")
    tree = html.fromstring(r.text)
    return tree.xpath("//div[@class='collapsible-body']//li/a/@href")


def get_data(url):
    locator_domain = "https://www.paintingwithatwist.com/"
    page_url = f"https://www.paintingwithatwist.com{url}"

    session = SgRequests()
    r = session.get(page_url + "contact")
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).replace(" Contact", "").strip()
    if r.url.find("contact") != -1:
        line = tree.xpath("//address/text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = line[0].strip()
        if street_address == "None" or street_address == "Address TBA":
            street_address = "<MISSING>"
        postal = line[1].split()[-1]
        city = line[1].split(",")[0].strip()
        state = line[1].split(",")[1].strip().split()[0]
    else:
        line = tree.xpath("//address/a/text()")
        line = list(filter(None, [l.strip() for l in line]))
        if line[0] != "Address TBA":
            street_address = line[0].strip()
        else:
            street_address = "<MISSING>"

        if len(line[-1].split(",")[1].strip().split()) == 2:
            city = line[-1].split(",")[0].strip()
            state = line[-1].split(",")[1].strip().split()[0].strip()
            postal = line[-1].split(",")[1].strip().split()[-1].strip()
        else:
            postal = "<MISSING>"
            city = line[-1].split(",")[0].strip()
            state = line[-1].split(",")[1].strip()

    country_code = "US"
    store_number = "<MISSING>"
    phone = tree.xpath("//a[contains(@href, 'tel')]/text()")
    if phone:
        phone = phone[0].strip()
    else:
        phone = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        ";".join(tree.xpath("//span[@class='worktime']/text()")[1:]).strip()
        or "<MISSING>"
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
