import csv
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


def fetch_data():
    out = []

    locator_domain = "https://www.bulknationusa.com"
    api_url = "https://www.bulknationusa.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[@class="col content-box-wrapper content-wrapper link-area-box link-type-text icon-hover-animation-pulsate"]'
    )
    for d in div:
        page_url = "".join(d.xpath(".//@data-link"))
        if page_url.find("https://www.bulknationusa.com") == -1:
            page_url = f"https://www.bulknationusa.com{page_url}"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath('//h1[@class="title-heading-left"]/text()'))

        street_address = (
            "".join(
                tree.xpath(
                    '//div[@class="fusion-layout-column fusion_builder_column fusion_builder_column_1_2 fusion-builder-column-3 fusion-one-half fusion-column-first 1_2"]//div[@class="content-container"]/text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(
                tree.xpath(
                    '//div[@class="fusion-layout-column fusion_builder_column fusion_builder_column_1_2 fusion-builder-column-3 fusion-one-half fusion-column-first 1_2"]//div[@class="content-container"]/text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )

        phone = (
            "".join(
                tree.xpath(
                    '//div[@class="fusion-layout-column fusion_builder_column fusion_builder_column_1_2 fusion-builder-column-4 fusion-one-half fusion-column-last 1_2"]//div[@class="content-container"]//a[contains(@href, "tel")]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )

        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        map_link = "".join(tree.xpath('//div[@class="fusion-text"]//iframe/@src'))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        location_type = "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[@class="fusion-layout-column fusion_builder_column fusion_builder_column_1_2 fusion-builder-column-4 fusion-one-half fusion-column-last 1_2"]//div[@class="content-container"]/p/text()'
                )
            )
            .replace("\n", "")
            .replace("Phone:", "")
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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
