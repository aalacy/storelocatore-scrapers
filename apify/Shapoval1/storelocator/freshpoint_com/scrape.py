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

    locator_domain = "https://www.freshpoint.com/"
    api_url = "https://www.freshpoint.com/find-your-location/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./div/p[@class="address"]]')
    for d in div:
        line = (
            "".join(
                d.xpath(
                    './/p[@class="address"]/text() | .//p[@class="address"]/a/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if line.find("1718 Elm") != -1:
            line = line.split("1718 Elm")[0].strip()
        line = (
            line.replace("Canada", "")
            .replace("B.C.", "BC")
            .replace("British Columbia,", "BC")
        )
        street_address = "<MISSING>"
        city = "<MISSING>"
        postal = "<MISSING>"
        state = "<MISSING>"

        if line.count(",") == 2:
            street_address = line.split(",")[0]
            city = line.split(",")[1].strip()
            state = line.split(",")[2].split()[0].strip()
            postal = " ".join(line.split(",")[2].split()[1:]).strip()
        if line.count(",") == 3:
            line = line.replace("  ", " ")

            street_address = line.split(",")[0] + " " + line.split(",")[1]
            city = line.split(",")[2].strip()
            state = line.split(",")[3].split()[0].strip()
            postal = " ".join(line.split(",")[3].split()[1:]).strip()

        phone = "".join(d.xpath('.//p[contains(text(), "Phone")]/text()')).split(
            "Phone"
        )[0]
        country_code = "US"
        if postal.find(" ") != -1:
            country_code = "CA"
        store_number = "<MISSING>"
        location_name = "".join(d.xpath('.//h3[@class="first"]//text()')).replace(
            "-", " -"
        )
        if street_address.find("10710") != -1:
            location_name = "".join(
                d.xpath('.//h3[@class="first secondAddress"]//text()')
            )
        page_url = (
            "".join(d.xpath(".//h3/a/@href"))
            or "https://www.freshpoint.com/find-your-location/"
        )
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        text = "".join(d.xpath('.//a[contains(@href, "maps")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"

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
