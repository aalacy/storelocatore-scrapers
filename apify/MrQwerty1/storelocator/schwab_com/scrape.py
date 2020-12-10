import csv

from concurrent.futures import ThreadPoolExecutor, as_completed
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
    r = session.get(
        "https://client.schwab.com/Public/BranchLocator/ViewAllBranches_abc.aspx?"
    )
    tree = html.fromstring(r.content)
    return tree.xpath("//a[@class='popup']/@href")


def get_data(page_url):
    session = SgRequests()

    locator_domain = "https://www.schwab.com/"

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    location_name = "".join(
        tree.xpath(
            "//h2[@id='ctl00_wpMngr_BranchDetail_BranchDetails_dynPageTitle']/text()"
        )
    ).strip()
    line = tree.xpath(
        "//p[@id='ctl00_wpMngr_BranchDetail_BranchDetails_brAddress']/text()"
    )
    line = list(filter(None, [l.strip() for l in line]))
    street_address = line[0]
    line = line[1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line[:2].strip()
    postal = line[2:].strip()
    country_code = "US"
    store_number = page_url.split("=")[-1]
    phone = tree.xpath("//span[@data-active='mobile']/text()")[0].strip()
    location_type = "Branch"
    latitude, longitude = "<MISSING>", "<MISSING>"

    _tmp = []
    tr = tree.xpath("//div[@id='hours-furl-content']/table[@class='hours']//tr")
    for t in tr:
        _tmp.append(" ".join(t.xpath("./td/text()")).strip())

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if hours_of_operation.count("Closed") == 7:
        return

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
    threads = []
    urls = get_urls()

    with ThreadPoolExecutor(max_workers=10) as executor:
        for url in urls:
            threads.append(executor.submit(get_data, url))

    for task in as_completed(threads):
        row = task.result()
        if row:
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
