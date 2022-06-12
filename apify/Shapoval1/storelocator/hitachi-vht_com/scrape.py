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

    locator_domain = "https://hitachi-vht.com/"
    page_url = "https://hitachi-vht.com/about-us/our-us-locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="col-md-6 col-sm-6"]')
    for d in div:

        location_name = (
            "".join(d.xpath('.//h2[@class="about-adress__title"]/text()'))
            .replace("\n", "")
            .strip()
        )
        location_type = "<MISSING>"
        street_address = (
            "".join(d.xpath('.//p[@class="about-adress__text"]/text()[1]'))
            .replace("\n", "")
            .strip()
            + ","
        )
        street_address = street_address.replace(",,", "")
        ad = (
            "".join(d.xpath('.//p[@class="about-adress__text"]/text()[2]'))
            .replace("\n", "")
            .replace("TX,", ",TX")
            .replace("MI,", ",MI")
            .strip()
        )

        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "<MISSING>"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        phone = (
            "".join(d.xpath('.//span[@class="about-adress__tel"]/a[1]/text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = "<MISSING>"

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
