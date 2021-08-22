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

    locator_domain = "https://www.kitandace.com"
    api_url = "https://www.kitandace.com/us/en/shoplocations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="js-store-item stores-list__item"]')

    for d in div:
        ft = "".join(d.xpath('.//div[@class="stores-data"]/p[1]/a/@href'))
        if ft.find("CLOSED") != -1 or ft.find("coming soon") != -1:
            continue
        slug = "".join(d.xpath('.//a[@class="button simple rare"]/@href'))
        latitude = "".join(d.xpath(".//@data-storelat"))
        longitude = "".join(d.xpath(".//@data-storelng"))
        page_url = f"{locator_domain}{slug}"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/text()"))
        location_type = "<MISSING>"
        ad = (
            "".join(tree.xpath('//div[@class="store-info store-info__address"]/text()'))
            .replace("\n", " ")
            .replace("The Village at Park Royal,", "")
            .strip()
        )

        street_address = ad.split(",")[0].strip()
        phone = "".join(
            tree.xpath('//a[@class="store-info store-info__phone"]/text()')
        ).strip()
        state = ad.split(",")[2].split()[0].strip()
        postal = " ".join(ad.split(",")[2].split()[1:]).strip()
        country_code = "CA"
        city = ad.split(",")[1].strip()
        store_number = "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h2[text()="Hours"]/following-sibling::table[@class="store-schedule"]//tr/td//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        tmpcls = (
            " ".join(tree.xpath('//h2[text()="Hours"]/following-sibling::p//text()'))
            .replace("\n", "")
            .strip()
        )
        if "temporarily closed" in tmpcls:
            hours_of_operation = "Temporarily closed"

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
