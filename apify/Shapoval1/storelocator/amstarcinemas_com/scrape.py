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

    locator_domain = "https://amstarcinemas.com"
    api_url = "https://amstarcinemas.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[contains(text(), "Get Details")]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"{locator_domain}{slug}"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        trees = html.fromstring(r.text)

        try:
            location_name = "".join(
                trees.xpath('//div[@class="location-main"]/h1/text()')
            )
        except:
            location_name = "<MISSING>"

        location_type = "<MISSING>"
        street_address = "".join(
            trees.xpath('//div[contains(@class, "address")]//text()[1]')
        )
        ad = (
            "".join(trees.xpath('//div[contains(@class, "address")]//text()[2]'))
            .replace("\n", "")
            .strip()
        )
        phone = (
            "".join(trees.xpath('//div[contains(@class, "address")]//text()[3]'))
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        if location_name.find("AmStar") != -1 or location_name.find("Amstar") != -1:
            location_type = "Amstar cinemas"
        if location_name.find("The Grand") != -1:
            location_type = "The Grand theatre"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
