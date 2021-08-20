import csv

from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgpostal import International_Parser, parse_address


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


def get_cities():
    cities = []
    session = SgRequests()
    r = session.get("https://www.popeyescanada.com/storelocator.html")
    tree = html.fromstring(r.text)
    states = tree.xpath("//table[@align='center']//td/a[contains(@href, 'loc')]/@href")
    for state in states:
        r = session.get(f"https://www.popeyescanada.com{state}")
        root = html.fromstring(r.text)
        cities += root.xpath("//div[@class='datagrid']/table//a/@href")

    return set(cities)


def translate(hours):
    hours = (
        hours.replace("à", "to")
        .replace("h00", ":00")
        .replace("Dimanche", "Sunday")
        .replace("Lundi", "Monday")
        .replace("Mardi", "Tuesday")
        .replace("Mercredi", "Wednesday")
        .replace("Jeudi", "Thursday")
        .replace("Vendredi", "Friday")
        .replace("Samedi", "Saturday")
    )
    return hours


def get_data(url):
    rows = []
    locator_domain = "https://www.popeyescanada.com/"
    if url.startswith("/"):
        page_url = f"https://www.popeyescanada.com{url}"
    else:
        page_url = f"{locator_domain}{url}"

    session = SgRequests()
    r = session.get(page_url)
    if r.status_code == 404:
        return []

    tree = html.fromstring(r.text)
    tr = tree.xpath("//div[@class='datagrid']//tr[@valign='top']")

    for t in tr:
        location_name = "".join(t.xpath(".//a[contains(@href,'maps')]//text()")).strip()
        if not location_name:
            location_name = "".join(t.xpath("./td[1]/p/strong/text()")).strip()
        line = t.xpath("./td[1]/p/text()")
        line = list(filter(None, [l.strip() for l in line]))
        if not line or len(line) == 1:
            continue

        index = 0
        for l in line:
            if "tel:" in l.lower():
                break
            index += 1
        else:
            index = len(line) - 1

        phone = line[index].lower().replace("tel:", "").strip()
        line = ", ".join(line[:index]).replace(",,", ",")
        adr = parse_address(International_Parser(), line)
        street_address = (
            f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )

        city = adr.city or "<MISSING>"
        state = adr.state or "<MISSING>"
        state = state.replace(".", "")
        postal = adr.postcode or "<MISSING>"
        country_code = "CA"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        days = t.xpath("./td[2]//text()")
        days = list(filter(None, [d.strip() for d in days]))
        times = t.xpath("./td[3]//text()")
        times = list(filter(None, [time.strip() for time in times]))

        for date, time in zip(days, times):
            _tmp.append(f"{date.strip()}: {time.strip()}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        hours_of_operation = translate(hours_of_operation)

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
        rows.append(row)

    return rows


def fetch_data():
    out = []
    urls = get_cities()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
