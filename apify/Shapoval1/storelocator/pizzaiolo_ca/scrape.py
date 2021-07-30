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
    locator_domain = "https://pizzaiolo.ca"
    api_url = "https://pizzaiolo.ca/locations"
    session = SgRequests()

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location-card"]')

    for d in div:
        ad = d.xpath('.//div[@class="address"]/text()')
        street_address = "".join(ad[0])
        ad = "".join(ad[1]).strip()
        city = ad.split(",")[0].strip()
        postal = " ".join(ad.split(",")[1].split()[1:]).strip()
        state = ad.split(",")[1].split()[0].strip()
        country_code = "CA"
        store_number = "<MISSING>"
        slug = "".join(d.xpath('.//a[contains(text(), "More Info")]/@href'))
        page_url = f"{locator_domain}{slug}"
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        location_name = "".join(
            tree.xpath('//h2[@class="heading-green inner-page-sub-title"]/text()')
        )
        text = "".join(tree.xpath('//a[contains(@href, "maps")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        if street_address.find("707") != -1 or street_address.find("104") != -1:
            latitude = (
                "".join(tree.xpath('//img[@class="img-polaroid"]/@src'))
                .split("center=")[1]
                .split(",")[0]
            )
            longitude = (
                "".join(tree.xpath('//img[@class="img-polaroid"]/@src'))
                .split("center=")[1]
                .split(",")[1]
                .split("&")[0]
            )
        location_type = "<MISSING>"
        hours_of_operation = (
            " ".join(tree.xpath('//table[@class="hours"]//tr/td/text()'))
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
