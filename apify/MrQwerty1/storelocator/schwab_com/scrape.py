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
    urls = []
    session = SgRequests()

    start = [
        "https://client.schwab.com/Public/BranchLocator/ViewAllBranches_abc.aspx?",
        "https://client.schwab.com/Public/BranchLocator/ViewAllBranches_defghil.aspx?",
        "https://client.schwab.com/Public/BranchLocator/ViewAllBranches_mn.aspx?",
        "https://client.schwab.com/Public/BranchLocator/ViewAllBranches_opqrstuvw.aspx?",
    ]

    for s in start:
        r = session.get(s)
        tree = html.fromstring(r.content)
        links = tree.xpath("//a[@class='popup']/@href")
        urls += links

    return urls


def get_data(page_url):
    session = SgRequests()

    locator_domain = "https://www.schwab.com/"

    r = session.get(page_url)
    if r.status_code == 404:
        return
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
