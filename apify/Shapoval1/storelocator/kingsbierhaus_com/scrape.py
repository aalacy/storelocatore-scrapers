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

    locator_domain = "https://www.kingsbierhaus.com"
    api_url = "https://www.kingsbierhaus.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="locationwrap"]')
    for d in div:

        page_url = "".join(d.xpath('.//a[text()="MORE INFO"]/@href'))
        location_name = "".join(d.xpath('.//h1[@class="locationtitle"]/text()'))
        location_type = "Restaurant"
        ad = (
            "".join(d.xpath('.//div[@class="location"]/p/text()'))
            .replace("\n", "")
            .strip()
        )

        street_address = " ".join(ad.split(",")[:-2])
        state = ad.split(",")[-1].split()[0].strip()
        postal = ad.split(",")[-1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[-2].strip()
        store_number = "<MISSING>"
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
        hours_of_operation = "<MISSING>"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
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
