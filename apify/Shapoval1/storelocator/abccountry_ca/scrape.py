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

    locator_domain = "https://www.abccountry.ca"
    api_url = "https://www.abccountry.ca/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//ul[@class="children"]/li/a')

    for d in div:

        page_url = "".join(d.xpath(".//@href"))

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath('//h1[@class="entry-title"]/text()'))
        location_type = "<MISSING>"
        ad = "".join(
            tree.xpath(
                '//div[@class="entry-content"]//a[contains(@href, "google")]/@href'
            )
        )
        street_address = "".join(
            tree.xpath('//div[@class="entry-content"]/p[1]//text()')
        )
        phone = (
            "".join(tree.xpath('//p[contains(text(), "(")]/text()'))
            .replace("\n", "")
            .strip()
        )
        city = (
            page_url.split("locations/")[1]
            .split("/")[1]
            .replace("/", "")
            .capitalize()
            .strip()
        )
        try:
            postal = " ".join(
                ad.split("/place/")[1]
                .split("/")[0]
                .split(",")[-1]
                .replace("+", " ")
                .split()[1:]
            )
        except:
            postal = "<MISSING>"
        country_code = "CA"
        state = page_url.split("locations/")[1].split("/")[0].strip()
        if state.find("-") != -1:
            state = state.split("-")[0].strip()
        state = state.upper().replace("ALBERTA", "AL")
        store_number = "<MISSING>"
        try:
            if ad.find("ll=") != -1:
                latitude = ad.split("ll=")[1].split(",")[0]
                longitude = ad.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = ad.split("@")[1].split(",")[0]
                longitude = ad.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = (
            " ".join(tree.xpath('//h2[text()="Hours:"]/following-sibling::p/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation.find("Special") != -1:
            hours_of_operation = hours_of_operation.split("Special")[0].strip()

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
