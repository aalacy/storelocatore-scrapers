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
    locator_domain = "https://zzeeks.com"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get("https://zzeeks.com/locations/", headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "elementor-column elementor-col-50")]')
    for d in div:

        page_url = "https://zzeeks.com/locations/"
        street_address = "".join(d.xpath('.//div/p[1]/span[@class="LrzXr"]/text()'))
        ad = "".join(d.xpath('.//div/p[2]/span[@class="LrzXr"]/text()')).strip()
        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        location_name = "".join(
            d.xpath('.//a[contains(@href, "tel")]/span/span/text()')
        )
        if location_name.find(":") != -1:
            location_name = location_name.split(":")[0].strip()
        if location_name.find("-") != -1:
            location_name = location_name.split("-")[0].strip()
        country_code = "US"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "Zesty Zzeeks Pizza & Wings"
        hours_of_operation = (
            " ".join(d.xpath(".//table//tr/td/span/text()")).replace("\n", "").strip()
        )
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/span/span/text()'))
        if phone.find(":") != -1:
            phone = phone.split(":")[1].strip()
        if phone.find("Ocotillo-") != -1:
            phone = phone.split("Ocotillo-")[1].strip()
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
