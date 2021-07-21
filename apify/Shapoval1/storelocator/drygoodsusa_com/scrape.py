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

    locator_domain = "https://www.drygoodsusa.com/"
    api_url = "https://www.drygoodsusa.com/Stores.aspx"

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }

    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="divStoresListStore"]/a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"{locator_domain}{slug}"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath('//div[@class="divStoresTitle"]/text()'))
        location_type = "<MISSING>"
        street_address = "".join(
            tree.xpath(
                '//div[@class="divStoreInfo"]/div[@class="divStoreInfoBox"]/div[1]/text()'
            )
        )
        if street_address.find("There are") != -1:
            street_address = street_address.split("There are")[0].strip()
        ad = "".join(tree.xpath('//div[@class="divStoreInfoBox"]/div[2]/text()'))
        phone = "".join(tree.xpath('//div[@class="divStoreInfoBox"]/div[3]/text()'))
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = page_url.split("=")[-1].strip()
        ll = (
            "".join(tree.xpath('//script[contains(text(), "maps.LatLng(")]/text()'))
            .split("LatLng(")[1]
            .split(");")[0]
            .strip()
        )
        latitude = ll.split(",")[0]
        longitude = ll.split(",")[1]
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//b[contains(text(), "STORE HOURS")]//text() | //b[contains(text(), "EFFECTIVE 6/12")]//text()'
                )
            )
            .replace("STORE HOURS", "")
            .replace("EFFECTIVE 6/12", "")
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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
