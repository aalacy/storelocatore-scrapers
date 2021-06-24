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


def get_urls():
    urls = []
    session = SgRequests()
    r = session.get("https://www.waitrose.com/content/waitrose/en/bf_home/bf.html")
    tree = html.fromstring(r.text)
    ids = tree.xpath("//select[@id='global-form-select-branch']/option/@value")
    for _id in ids:
        if not _id:
            continue
        urls.append(
            f"https://www.waitrose.com/content/waitrose/en/bf_home/bf/{_id}.html"
        )

    return urls


def get_js(lat, lng, _id):
    session = SgRequests()
    r = session.get(
        f"https://www.waitrose.com/shop/NearestBranchesCmd?latitude={lat}&longitude={lng}"
    )
    try:
        js = r.json()["branchList"]
    except:
        js = []
    out = dict()
    for j in js:
        if str(j.get("branchId")) == _id:
            out = j
            break

    return out


def get_data(page_url):
    locator_domain = "https://www.waitrose.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    latitude = "".join(tree.xpath("//a[@data-lat]/@data-lat"))
    longitude = "".join(tree.xpath("//a[@data-long]/@data-long"))
    store_number = page_url.split("/")[-1].replace(".html", "")
    country_code = "GB"

    j = get_js(latitude, longitude, store_number)
    if j:
        street_address = (
            f"{j.get('addressLine1')} {j.get('addressLine2') or ''}".strip()
            or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postCode") or "<MISSING>"
        location_name = j.get("branchName") or "<MISSING>"
        phone = j.get("phoneNumber") or "<MISSING>"
        location_type = j.get("branchDesc") or "<MISSING>"
    else:
        location_name = "".join(
            tree.xpath("//h1[contains(text(), 'Welcome to')]/text()")
        )
        if "little" in location_name.lower():
            location_type = "Little Waitrose"
        else:
            location_type = "Standard Branch"
        location_name = location_name.split("Welcome to")[-1].strip()
        if not location_name:
            location_name = "<MISSING>"
        line = tree.xpath("//div[@class='col branch-details']/p/text()")
        line = list(filter(None, [l.strip() for l in line]))
        if not line:
            return
        if line[-2] == "U.A.E." or line[-2] == "677":
            return

        phone = line.pop()
        adr = parse_address(International_Parser(), ", ".join(line))
        street_address = (
            f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )

        city = adr.city or "<MISSING>"
        state = adr.state or "<MISSING>"
        postal = adr.postcode or "<MISSING>"

    _tmp = []
    tr = tree.xpath("//div[@class='tab' and not(@id)]//tr")
    for t in tr:
        day = "".join(t.xpath("./td[1]//text()")).strip()
        time = "".join(t.xpath("./td[last()]//text()")).strip()
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
    s = set()
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                check = tuple(row[2:7])
                if check not in s:
                    s.add(check)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
