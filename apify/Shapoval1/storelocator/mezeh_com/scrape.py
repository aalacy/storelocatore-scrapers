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
    locator_domain = "https://mezeh.com"
    page_url = "https://mezeh.com/locations/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[@class="column_attr clearfix align_left mobile_align_left"]'
    )
    for j in div:
        coming_soon = "".join(j.xpath(".//h3/strong/text()"))
        if coming_soon.find("coming soon") != -1:
            continue

        ad = j.xpath(".//a[1]/h5/text()")
        ad = list(filter(None, [a.strip() for a in ad]))
        street_address = "".join(ad[0])
        line = ad[1]
        city = "".join(line.split(",")[0])
        line = line.split(",")[1].strip()
        postal = "".join(line.split()[1])
        state = "".join(line.split()[0])
        try:
            phone = "".join(ad[2])
        except IndexError:
            phone = "<MISSING>"
        hours_of_operation = ";".join(ad[3:]) or "Closed"
        country_code = "US"
        store_number = "<MISSING>"
        page_url = "".join(j.xpath(".//a[1]/@href")) or "<MISSING>"
        location_name = (
            "".join(j.xpath(".//a/h4/text()")).replace("’", "").replace("‘", "")
            or "<MISSING>"
        )

        latitude = "".join(j.xpath('.//div[@class="marker"]/@data-lat')) or "<MISSING>"
        longitude = "".join(j.xpath('.//div[@class="marker"]/@data-lng')) or "<MISSING>"
        location_type = "<MISSING>"

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
