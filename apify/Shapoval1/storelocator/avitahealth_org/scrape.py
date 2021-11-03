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

    locator_domain = "https://avitahealth.org"
    page_url = "https://avitahealth.org/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="col-md-4 mb-3"]')
    for d in div:

        location_name = "".join(d.xpath('.//p[@class="font-weight-bold mb-0"]/text()'))
        if location_name.find("Avita") == -1:
            location_name = "Avita" + " " + location_name
        location_type = "<MISSING>"
        street_address = "".join(d.xpath('.//p[@class="mb-0"]/text()[1]'))
        ad = "".join(d.xpath('.//p[@class="mb-0"]/text()[2]')).replace("\n", "").strip()
        phone = (
            "".join(d.xpath('.//a[contains(@href, "tel")]/text()')).replace(
                "4419", "419"
            )
            or "<MISSING>"
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        if city.find("Crestline") != -1:
            state = "OH"
        store_number = "<MISSING>"
        session = SgRequests()
        r = session.get(
            "https://avitahealth.org/wp-content/themes/avita/js/google-map.js",
            headers=headers,
        )

        slug = street_address.split()[0].strip()
        text = r.text.split(slug)[1].split("z/")[0]
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
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
