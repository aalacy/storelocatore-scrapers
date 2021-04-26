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


def get_params():
    params = []
    session = SgRequests()
    r = session.get(
        "https://www.magnet.co.uk/Views/Pages/StudioPages/Services/GoogleMapStores/Service.ashx?findPage=60&language=en"
    )
    js = r.json()["stores"]
    for j in js:
        params.append((j.get("store_url"), (j.get("lat"), j.get("lng"))))

    return params


def get_hours(page_url):
    _tmp = []
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    days = tree.xpath(
        "//h2[./strong[contains(text(), 'Opening Hours')]]/following-sibling::dl/dt/text()"
    )
    times = tree.xpath(
        "//h2[./strong[contains(text(), 'Opening Hours')]]/following-sibling::dl/dd//text()"
    )

    for d, t in zip(days, times):
        if t.find("(") != -1:
            t = t.split("(")[0]
        t = t.replace("*", "").replace("till", "-").strip()
        if t.lower().find("virt") != -1 or not t:
            t = "Closed"
        if t.lower().find("call") != -1 or t.lower().find("closed") != -1:
            t = "Closed"
        if t.lower().find("appointment") != -1 or t.lower().find("christmas") != -1:
            t = "Closed"

        _tmp.append(f"{d.strip()}: {t}")

    hoo = ";".join(_tmp) or "<MISSING>"

    if hoo.count("Closed") == 7:
        hoo = "Closed"

    return hoo


def get_data(params):
    page_url = params[0]
    latitude, longitude = params[1]
    if latitude == 0 and longitude == 0:
        latitude, longitude = "<MISSING>", "<MISSING>"
    locator_domain = "https://www.magnet.co.uk/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    line = " ".join(
        ", ".join(tree.xpath("//*[@itemprop='address']//text()")).split()
    ).split(",")
    line = list(filter(None, [l.strip() for l in line]))
    line = ", ".join(line)

    line = line.replace(" -", "").strip()
    if line.find("Tel:") != -1:
        line = line.split("Tel:")[0].strip()
    if line.find("appointment") != -1:
        line = line.split(".")[-1].strip()

    if line == "<MISSING>":
        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
    else:
        line = line.replace(", ,", ",").strip()
        postal = " ".join(line.split()[-2:]).replace(",", "").strip()
        line = line.replace(postal, "").strip()
        if line.endswith(","):
            line = line[:-1].replace(", ,", ", ")
        adr = parse_address(International_Parser(), line, postcode=postal)
        street_address = (
            f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )

        city = adr.city or "<MISSING>"
        state = adr.state or "<MISSING>"
        postal = adr.postcode or "<MISSING>"
    country_code = "GB"
    store_number = "<MISSING>"
    location_name = "".join(tree.xpath("//h1[@itemprop='name']/text()")).strip()

    try:
        phone = (
            tree.xpath("//a[@itemprop='telephone']/@href")[0]
            .replace("tel:", "")
            .replace("Retail", "")
            .strip()
        )
        if phone.find("Department") != -1:
            phone = phone.split("Department")[-1].replace(".", "").strip()
        elif phone.find("counter") != -1:
            phone = phone.split("counter")[-1].strip()
        elif phone.find("-") != -1:
            phone = phone.split("-")[-1].strip()
        elif phone.find("kitchen") != -1:
            phone = phone.split("kitchen")[0].strip()
        elif phone.find(")") != -1:
            phone = phone.split(")")[-1].strip()
        elif phone.find("find-a-showroom") != -1:
            phone = "<MISSING>"
        elif phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
    except IndexError:
        phone = "<MISSING>"

    location_type = "<MISSING>"
    hours_of_operation = get_hours(page_url)

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
    params = get_params()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, param): param for param in params}
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
