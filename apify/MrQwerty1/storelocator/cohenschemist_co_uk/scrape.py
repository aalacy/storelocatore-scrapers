import csv

from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address, International_Parser


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
    ids = set()
    session = SgRequests()
    r = session.get("https://www.cohenschemist.co.uk/mycohens/directory/")
    tree = html.fromstring(r.text)
    links = tree.xpath("//div[contains(@onclick, 'popup_BranchDetails(')]/@onclick")
    for l in links:
        _id = l.split("'")[1]
        ids.add(_id)

    return ids


def get_data(store_number):
    locator_domain = "https://www.cohenschemist.co.uk/"
    page_url = "https://www.cohenschemist.co.uk/mycohens/directory/"

    data = {"task": "popup_BranchDetails", "BranchID": store_number}

    session = SgRequests()
    r = session.post(
        "https://www.cohenschemist.co.uk/wp-admin/admin-ajax.php?action=mycohens_ajax",
        data=data,
    )
    tree = html.fromstring(r.text)

    location_name = tree.xpath("//strong/text()")[0].strip()
    line = tree.xpath("./text()")
    line = list(filter(None, [l.strip() for l in line]))
    phone = line[1].replace("|", "").strip() or "<MISSING>"
    line = line[0].upper()
    postal = line.split(",")[-1].strip()
    line = ",".join(line.split(",")[:-1]).strip()

    adr = parse_address(International_Parser(), line, postcode=postal)
    street_address = (
        f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
            "None", ""
        ).strip()
        or "<MISSING>"
    )

    if len(street_address) < 5:
        street_address = line.split(",")[0].strip()

    city = adr.city or "<MISSING>"
    state = adr.state or "<MISSING>"
    postal = adr.postcode or "<MISSING>"
    country_code = "GB"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    tr = tree.xpath("//tr[./td]")

    for t in tr:
        day = "".join(t.xpath("./td[1]/text()")).strip()
        start = "".join(t.xpath("./td[2]/text()")).strip()
        close = "".join(t.xpath("./td[3]/text()")).strip()
        if start == close:
            _tmp.append(f"{day}: Closed")
        else:
            if close != "Closed":
                _tmp.append(f"{day}: {start} & {close}")
            else:
                _tmp.append(f"{day}: {start}")
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
