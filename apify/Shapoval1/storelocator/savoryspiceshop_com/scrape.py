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

    locator_domain = "https://www.savoryspiceshop.com"
    api_url = "https://www.savoryspiceshop.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[contains(@id, "store")]')

    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"{locator_domain}{slug}"
        if page_url.find("st. P") != -1:
            page_url = page_url.replace("st. Petersburg.html", "st.%20Petersburg.html")
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = (
            "".join(tree.xpath('//h1[@style="font-weight: bold;"]//text()'))
            .replace("\n", "")
            .strip()
        )
        location_type = "<MISSING>"
        adr = tree.xpath(
            '//h3[contains(text(), "Address")]/following-sibling::p[1]/text()'
        )
        ad = "".join(adr[-1]).replace("\n", "").strip()
        street_address = "<MISSING>"
        if len(adr) == 2:
            street_address = "".join(adr[0])
        if len(adr) == 3:
            street_address = "".join(adr[0]) + " " + "".join(adr[1])
        if len(adr) == 4:
            street_address = (
                "".join(adr[0]) + " " + "".join(adr[1]) + " " + "".join(adr[2])
            )
        street_address = street_address.replace("\n", "").strip()

        phone = (
            "".join(
                tree.xpath(
                    '//h3[contains(text(), "Contact")]/following-sibling::p[1]/text()[1]'
                )
            )
            .replace("P:", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        ll = (
            "".join(tree.xpath('//script[contains(text(), "googleMap")]/text()'))
            .split("center: '(")[1]
            .split(")',")[0]
            .strip()
        )

        latitude = ll.split(",")[0].strip()
        longitude = ll.split(",")[1].strip()
        if latitude == "0.0000000":
            latitude = "<MISSING>"
        if longitude == "0.0000000":
            longitude = "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h3[contains(text(), "Hours")]/following-sibling::p[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("hours:") != -1:
            hours_of_operation = hours_of_operation.split("hours:")[1].strip()
        if hours_of_operation.find("Spice Experts.") != -1:
            hours_of_operation = hours_of_operation.split("Spice Experts.")[1].strip()
        if hours_of_operation.find("*") != -1:
            hours_of_operation = hours_of_operation.split("*")[0].strip()
        if hours_of_operation.find("We will be OPEN") != -1:
            hours_of_operation = hours_of_operation.split("We will be OPEN")[0].strip()
        if hours_of_operation.find("or on our website.") != -1:
            hours_of_operation = hours_of_operation.split("or on our website.")[
                1
            ].strip()
        if hours_of_operation.find("HOLIDAY NOTICE:") != -1:
            hours_of_operation = hours_of_operation.split("HOLIDAY NOTICE:")[0].strip()
        hours_of_operation = (
            hours_of_operation.replace("Curbside Pick Up Available", "")
            .replace("SPRING HOURS", "")
            .replace("?", "")
            .replace("STORE HOURS", "")
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
