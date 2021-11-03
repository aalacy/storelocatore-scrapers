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

    locator_domain = "https://hotchickentakeover.com"
    api_url = "https://hotchickentakeover.com/find-us/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)

    div = tree.xpath('//article[@class="location-card"]')

    for d in div:

        page_url = "".join(d.xpath('.//div[@class="location-card-header"]/a/@href'))
        location_name = (
            "".join(d.xpath('.//div[@class="location-card-header"]//h3//text()'))
            + " "
            + "".join(d.xpath('.//div[@class="location-card-header"]//h4//text()'))
        )
        location_type = "<MISSING>"
        ad = d.xpath('.//div[@class="location-address"]/p//text()')
        ad = list(filter(None, [a.strip() for a in ad]))

        street_address = "".join(ad[0])
        if len(ad) > 2:
            street_address = (
                "".join(ad[0])
                + " "
                + "".join(ad[1]).replace("[Inside the North Market]", "").strip()
            )
        adr = "".join(ad[-1])
        state = adr.split(",")[1].split()[0].strip()
        postal = adr.split(",")[1].split()[1].strip()
        country_code = "US"
        city = adr.split(",")[0].strip()
        store_number = "<MISSING>"
        text = "".join(d.xpath('.//a[text()="GET DIRECTIONS"]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "".join(d.xpath('.//div[@class="location-phone"]/p//text()'))
        hours_of_operation = (
            " ".join(d.xpath('.//div[@class="day-hours"]/p//text()'))
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
