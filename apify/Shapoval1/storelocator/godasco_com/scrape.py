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
    r = session.get("http://godasco.com/locations.asp", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath('//a[@class="learn-more"]/@href')


def get_data(url):
    locator_domain = "http://godasco.com/"
    page_url = f"{locator_domain}{url}"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="col-md-5"]/h5[1]')
    for d in div:

        location_name = " ".join(d.xpath(".//text()")).replace("\r\n", "").strip()
        street_address = (
            "".join(d.xpath(".//following-sibling::p[1]/text()[1]")) or "<MISSING>"
        )

        ad = (
            "".join(d.xpath(".//following-sibling::p[1]/text()[2]"))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if ad == "<MISSING>":
            ad = (
                "".join(d.xpath(".//following-sibling::p[2]/text()"))
                .replace("\n", "")
                .strip()
            )
        ad = ad.replace(",", "")
        city = " ".join(ad.split()[:-2]).strip()
        state = ad.split()[-2].strip()
        postal = ad.split()[-1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(
                d.xpath('.//following-sibling::p[contains(text(), "Phone")]/text()')
            )
            .replace("Phone#:", "")
            .strip()
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = "".join(
                d.xpath(
                    './/following-sibling::p[1]/b[contains(text(), "Phone")]/following-sibling::text()[1]'
                )
            ).strip()

        location_type = "DASCO"
        hours_of_operation = d.xpath(".//following-sibling::p[last()]//text()")
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation).replace("â", "-")
        map_link = "".join(d.xpath(".//preceding::iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

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
