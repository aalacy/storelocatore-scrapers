import csv
import json
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

    locator_domain = "https://www.thepizzapress.com"
    api_url = "https://www.thepizzapress.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="columns-tab-3 columns-desk-3"]/p[./a]/a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = slug
        if page_url.find("http") == -1:
            page_url = f"{locator_domain}{slug}"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath('//h1[@class="page-header-title inherit"]/text()'))
            or "<MISSING>"
        )
        location_type = "Restaurant"
        street_address = (
            "".join(
                tree.xpath('//p[@class="company-info-address"]/span/span[1]/text()')
            )
            or "<MISSING>"
        )
        state = (
            "".join(
                tree.xpath('//p[@class="company-info-address"]/span/span[3]/text()')
            )
            or "<MISSING>"
        )
        postal = (
            "".join(
                tree.xpath('//p[@class="company-info-address"]/span/span[4]/text()')
            )
            or "<MISSING>"
        )
        country_code = "USA"
        city = (
            "".join(
                tree.xpath('//p[@class="company-info-address"]/span/span[2]/text()')
            )
            or "<MISSING>"
        )
        if city.find("(Downtown)") != -1:
            city = city.replace("(Downtown)", "").strip()

        store_number = "<MISSING>"
        try:
            latitude = (
                "".join(tree.xpath('//script[contains(text(), "latitude")]/text()'))
                .split('latitude":')[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "latitude")]/text()'))
                .split('longitude":')[1]
                .split("}")[0]
                .strip()
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(tree.xpath('//span[@class="company-info-phone"]//a/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(tree.xpath("//ol//text()")).replace("\n", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>":
            jsblock = "".join(
                tree.xpath('//script[contains(text(), "latitude")]/text()')
            )
            js = json.loads(jsblock)
            location_name = js[0].get("name")
            street_address = js[0].get("address").get("streetAddress")
            state = js[0].get("address").get("addressRegion")
            postal = js[0].get("address").get("postalCode")
            country_code = "USA"
            phone = js[0].get("telephone")
            city = js[0].get("address").get("addressLocality")
            latitude = js[0].get("geo").get("latitude")
            longitude = js[0].get("geo").get("longitude")
            hours = js[0].get("openingHoursSpecification")
            tmp = []
            for h in hours:
                days = (
                    "".join(h.get("dayofWeek")[0])
                    + "-"
                    + "".join(h.get("dayofWeek")[-1])
                )
                opens = h.get("opens")
                closes = h.get("closes")
                line = f"{days} {opens} {closes}"
                tmp.append(line)
            hours_of_operation = ";".join(tmp) or "<MISSING>"

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
