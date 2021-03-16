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
    locator_domain = "https://shsalons.com"
    page_url = "https://shsalons.com/pages/sh-salons-locations"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    block = tree.xpath(
        "//div[contains(@class, 'sc-pZopv bjKdkd')] [position()>1 and position()<last()]"
    )
    for b in block:
        location_name = (
            "".join(b.xpath(".//img/@src"))
            .split("--")[1]
            .split(".")[0]
            .replace("SH-Facebook", "")
            .replace("-", " ")
            .replace("copy", "")
            .strip()
        )
        if location_name.find("02") != -1:
            location_name = (
                "".join(b.xpath('.//span[@class="sc-ptSuy fnmilh pf-df12a227"]/text()'))
                .replace("\n", "")
                .split("-")[0]
                .strip()
            )
        if location_name.find("Katy") == -1 and location_name.find("SH") == -1:
            location_name = location_name + " " + "Location"
        ad = b.xpath(".//span[contains(text(), 'Phone')]//text()")
        phone = "".join(ad[0]).split("Phone:")[1].strip()
        street_address = "".join(ad[1]).split("Add:")[1].strip()
        ad = "".join(ad[2:]).replace("\n", "")
        if ad.find(")") != -1:
            ad = ad.split(")")[1]
        if ad.find("HEB") != -1:
            ad = ad.split("HEB")[0]
        if ad.find("Kroger") != -1:
            ad = ad.split("Kroger")[0]
        if ad.find("Katy") != -1:
            ad = ad.replace("—", "— ")
        city = ad.split(",")[0]
        state = ad.split(",")[1].split()[0]
        postal = ad.split(",")[1].split()[-1]
        country_code = "US"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            " ".join(
                b.xpath(
                    ".//span[contains(text(), 'HOURS')]/following::span[1]/text() | .//span[contains(text(), 'SH')]/following::span[1]/text()"
                )
            )
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
