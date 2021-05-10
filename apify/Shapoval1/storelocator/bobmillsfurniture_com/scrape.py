import csv
import json
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
    r = session.get("https://www.bobmillsfurniture.com/api/rest/pages/")
    jsblock = r.text.replace("['", "").replace("']", "")
    js = json.loads(jsblock)
    slugs = []
    for j in js:
        sl = "".join(j.get("request_url"))
        if sl == "home":
            continue
        if sl.find("locations") == -1:
            continue
        sl = sl.split("/")[1]
        slugs.append(sl)
    return slugs


def get_data(slug):

    locator_domain = "https://www.bobmillsfurniture.com"

    api_url = f"https://www.bobmillsfurniture.com/api/rest/pages/locations%2F{slug}"

    session = SgRequests()

    r = session.get(api_url)
    div = (
        r.text.split(
            "<!-- ==================== Contact Block (block-1) ==================== -->"
        )[1]
        .replace("\\r", "")
        .replace("\\n", "")
        .replace("\\t", "")
        .replace("\\", "")
    )
    tree = html.fromstring(div)
    street_address = (
        "".join(
            tree.xpath(
                '//div[@class="avb-typography__paragraph dsg-tools-main-paragraph dsg-tools-color-dark dsg-contact-1__address"]/span[@class="dsg-contact-1__address-line"][1]/text()'
            )
        )
        .replace("\n", "")
        .strip()
    )
    ad = (
        "".join(
            tree.xpath(
                '//div[@class="avb-typography__paragraph dsg-tools-main-paragraph dsg-tools-color-dark dsg-contact-1__address"]/span[@class="dsg-contact-1__address-line"][2]/text()'
            )
        )
        .replace("\n", "")
        .strip()
    )
    page_url = f"https://www.bobmillsfurniture.com/locations/{slug}"
    city = ad.split(",")[0].strip()
    state = ad.split(",")[1].split()[0].strip()
    postal = ad.split(",")[1].split()[1].strip()
    country_code = "US"
    store_number = "<MISSING>"
    location_name = "".join(tree.xpath("//h1/text()"))
    phone = "".join(tree.xpath('//avb-link[contains(@data-href, "tel")]/text()'))
    text = "".join(tree.xpath('//avb-link[contains(@data-href, "/maps/")]/@data-href'))
    try:
        if text.find("ll=") != -1:
            latitude = text.split("ll=")[1].split(",")[0]
            longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//h2[contains(text(), "Store Hours")]/following-sibling::ul/li/text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    if hours_of_operation == "<MISSING>":
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h2[contains(text(), "Pickup")]/following-sibling::ul/li/text()'
                )
            )
            .replace("\n", "")
            .strip()
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
