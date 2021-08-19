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

    locator_domain = "https://www.breadwinnerscafe.com"
    page_url = "https://www.breadwinnerscafe.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="_3oqF5"]/span')

    for d in div:

        location_name = "".join(d.xpath(".//text()"))
        if location_name.find("CATERING") != -1 or location_name.find("emplo") != -1:
            continue
        location_type = "<MISSING>"
        street_address = "".join(
            d.xpath('.//following::h2[@style="font-size:13px"][1]//text()')
        )
        ad = "".join(d.xpath('.//following::h2[@style="font-size:13px"][2]//text()'))
        phone = (
            "".join(d.xpath('.//following::h2[@style="font-size:13px"][3]//text()'))
            .replace("P:", "")
            .replace(" - ", "-")
            .strip()
        )
        state = ad.split(",")[1].strip().capitalize()
        postal = ad.split(",")[2].strip().capitalize()
        country_code = "US"
        city = ad.split(",")[0].strip().capitalize()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = (
            "".join(d.xpath('.//following::span[@style="font-weight:bold"][1]//text()'))
            + " "
            + "".join(
                d.xpath('.//following::span[@style="font-weight:bold"][2]//text()')
            )
        )
        hours_of_operation = (
            hours_of_operation
            + " "
            + "".join(
                d.xpath('.//following::span[@style="font-weight:bold"][3]//text()')
            )
            + " "
            + "".join(
                d.xpath('.//following::span[@style="font-weight:bold"][4]//text()')
            )
        )
        hours_of_operation = (
            hours_of_operation.replace("​ ​ ", "")
            .replace("​ ", "")
            .replace("CATERING", "")
            .strip()
        )
        if location_name.find("NORTHPARK CENTER") != -1:
            hours_of_operation = "".join(
                d.xpath('.//following::span[contains(text(), "SUN 9A-5P")]/text()')
            )
            street_address = "".join(
                d.xpath('.//following::div[@id="comp-jmjbydnm"]/h2[1]//text()')
            )
            ad = "".join(
                d.xpath('.//following::div[@id="comp-jmjbydnm"]/h2[2]//text()')
            )
            state = ad.split(",")[1].strip().capitalize()
            postal = ad.split(",")[2].strip().capitalize()
            country_code = "US"
            city = ad.split(",")[0].strip().capitalize()
            phone = (
                "".join(d.xpath('.//following::div[@id="comp-jmjbydnm"]/h2[3]//text()'))
                .replace("P:", "")
                .replace(" - ", "-")
                .strip()
            )

        hours_of_operation = (
            hours_of_operation.replace("BRUNCH:", "").replace("BRUNCH", "").strip()
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
