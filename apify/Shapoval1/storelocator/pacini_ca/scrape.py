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

    locator_domain = "https://pacini.com/"
    api_url = "https://pacini.com/en/restaurants/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="wpb_wrapper"]/ul/li/a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://pacini.com{slug}"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(
            tree.xpath('//span[@class="blanc"]/text() | //h1/text()')
        )
        street_address = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        city = "<MISSING>"
        ad = (
            " ".join(tree.xpath('//a[@href="#us_map_1"]/text()'))
            .replace("\n", "")
            .strip()
        )
        ad = ad.replace("(Québec)", ",Québec")
        if ad.count(",") == 1:
            street_address = " ".join(ad.split(",")[0].split()[:-1]).strip()
            city = ad.split(",")[0].split()[-1]
            state = ad.split(",")[1].split()[0]
            postal = " ".join(ad.split(",")[1].split()[1:]).strip()
        if ad.count(",") == 2:
            street_address = (
                ad.split(",")[0] + " ".join(ad.split(",")[1].split()[:-1]).strip()
            )
            city = ad.split(",")[1].split()[-1]
            state = ad.split(",")[2].split()[0]
            postal = " ".join(ad.split(",")[2].split()[1:]).strip()
        location_type = "<MISSING>"
        phone = (
            "".join(
                tree.xpath(
                    '//a[contains(@href, "tel:")]/text() | //div[./i[@class="fas fa-mobile-alt"]]/following-sibling::div//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        phone = (
            phone.replace("RESERVATION", "")
            .replace("ONLINE", "")
            .replace("Online Reservation", "")
            .replace("Book online", "")
            .replace("9733450 359-9733", "9733")
            or "<MISSING>"
        )
        country_code = "CA"
        store_number = "<MISSING>"
        map_link = "".join(tree.xpath('//iframe[@loading="lazy"]/@src'))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[./i[@class="far fa-clock"]]/following-sibling::div//p/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        tmpclz = " ".join(tree.xpath('//div[@class="wpb_wrapper"]/p/text()')).replace(
            "\n", ""
        )
        if tmpclz.find("temporarily close") != -1:
            hours_of_operation = "temporarily close"
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
