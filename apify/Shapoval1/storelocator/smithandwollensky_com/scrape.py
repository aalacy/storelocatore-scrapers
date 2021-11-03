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

    locator_domain = "https://www.smithandwollensky.com"
    api_url = "https://www.smithandwollensky.com/our-restaurants/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location-box"]')
    for d in div:
        slug = "".join(d.xpath("./a/@href"))

        page_url = f"{api_url}{slug}"

        location_name = "".join(d.xpath(".//h3/text()"))
        location_type = "restaurant"
        street_address = "".join(d.xpath('.//div[@class="info address"]/p[2]/text()'))
        ad = "".join(d.xpath('.//div[@class="info address"]/p[4]/text()')).strip()

        if ad.find("Taipei") != -1:
            continue

        phone = "".join(d.xpath('.//div[@class="info address"]/p[1]/text()'))
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1]
        country_code = "US"
        if street_address.find("Adelphi") != -1:
            street_address = (
                street_address
                + " "
                + "".join(d.xpath('.//div[@class="info address"]/p[3]/text()'))
            )
            state = "<MISSING>"
            postal = " ".join(ad.split(",")[1].split()[-2:])
            country_code = "UK"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        link = "".join(tree.xpath('//a[./div/p[contains(text(), "Book Now")]]/@href'))
        if link.find("columbus") != -1 or link.find("wellesley") != -1:
            link = ""
        if link:
            session = SgRequests()
            r = session.get(link, headers=headers)
            tree = html.fromstring(r.text)

            map_link = "".join(tree.xpath("//iframe/@src"))

            latitude = (
                map_link.split("!1d")[1]
                .strip()
                .split("!")[0]
                .replace("3222", "22")
                .strip()
            )
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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
