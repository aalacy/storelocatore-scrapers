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

    locator_domain = "https://www.cheesetique.com"
    api_url = "https://www.cheesetique.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[./div[@class="card__media"]]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))

        page_url = f"{locator_domain}{slug}"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/text()")).replace("\n", "").strip()
        location_type = "Restaurant"
        street_address = (
            "".join(
                tree.xpath('//a[contains(@href, "tel")]/preceding-sibling::a/text()[1]')
            )
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        ad = (
            "".join(
                tree.xpath('//a[contains(@href, "tel")]/preceding-sibling::a/text()[2]')
            )
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = " ".join(ad.split(",")[1].split()[1:]).strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        latitude = "".join(tree.xpath("//div/@data-gmaps-lat"))
        longitude = "".join(tree.xpath("//div/@data-gmaps-lng"))
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()'))
        hours_of_operation = (
            " ".join(tree.xpath('//p[./u/strong[text()="RESTAURANT"]]//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = hours_of_operation.replace("RESTAURANT", "").strip()
        if hours_of_operation.find("(") != -1:
            hours_of_operation = hours_of_operation.split("(")[0].strip()

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
