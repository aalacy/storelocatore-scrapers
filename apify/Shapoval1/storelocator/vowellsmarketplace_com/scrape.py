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

    locator_domain = "https://vowellsmarketplace.com/"
    api_url = "https://vowellsmarketplace.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//ul[@id="menu-main-1"]/li[./a[contains(text(), "Locations")]]/a/following-sibling::ul/li/a'
    )

    for d in div:

        page_url = "".join(d.xpath(".//@href"))

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(
            tree.xpath(
                '//div[@class="motopress-image-obj motopress-text-align-center motopress-margin-top-10"]/img/@title'
            )
        ).replace("Header", "")
        location_type = "Vowells Marketplace"
        street_address = "".join(
            tree.xpath(
                '//div[@class="mp-span12 motopress-clmn mpce-dsbl-margin-left mpce-dsbl-margin-right"]/div/h5[1]//text()'
            )
        )
        ad = (
            "".join(
                tree.xpath(
                    '//div[@class="mp-span12 motopress-clmn mpce-dsbl-margin-left mpce-dsbl-margin-right"]/div/h5[2]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )

        phone = (
            "".join(tree.xpath('//span[contains(text(), "Phone")]/text()'))
            .replace("Phone:", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        hours_of_operation = (
            " ".join(tree.xpath('//span[contains(text(), "pm")]/text()'))
            .replace("Hours:", "")
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation.find("Online") != -1:
            hours_of_operation = hours_of_operation.split("Online")[0].strip()
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(tree.xpath('//span[contains(text(), "am")]/text()'))
                .replace("Hours:", "")
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
