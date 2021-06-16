import csv
from lxml import html
from sgrequests import SgRequests
from concurrent import futures


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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    urls = []
    for i in range(1, 4):
        r = session.get(
            f"https://trcstaffing.com/page/{i}/?s&post_type=locations#038;post_type=locations",
            headers=headers,
        )
        tree = html.fromstring(r.text)
        dd = tree.xpath("//h2/a")
        for d in dd:
            pages_url = "".join(d.xpath(".//@href"))
            urls.append(pages_url)
    return urls


def get_data(url):
    locator_domain = "https://trcstaffing.com/"
    page_url = "".join(url)
    if page_url.count("/") == 5:
        return
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()"))
    adr = tree.xpath(
        '//h2[text()="Address"]/following-sibling::div[1]//div[@class="wpb_wrapper"]/div[1]/p/text()'
    )
    street_address = "".join(adr[0]).strip()
    if len(adr) > 2:
        street_address = " ".join(adr[:-1]).replace("\n", "").strip()
    ad = "".join(adr[-1])
    city = ad.split(",")[0].strip()
    state = ad.split(",")[1].split()[0].strip()
    postal = ad.split(",")[1].split()[1].strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                '//h2[text()="Address"]/following-sibling::div[1]//div[@class="wpb_wrapper"]/div[2]//text()'
            )
        )
        .replace("Phone:", "")
        .strip()
    )
    location_type = "TRC staffing"
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//h2[text()="Hours"]/following-sibling::div[1]//table//tr/td//text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    latitude = "<MISSING>"
    longitude = "<MISSING>"

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
