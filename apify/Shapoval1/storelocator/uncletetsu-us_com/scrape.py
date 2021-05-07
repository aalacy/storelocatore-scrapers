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

    locator_domain = "https://www.uncletetsu-us.com"
    page_url = "https://www.uncletetsu-us.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//table[@class="views-table views-view-table cols-0"]//tr')
    for d in div:

        location_name = "".join(d.xpath('.//div[@class="title"]/text()'))
        ad = (
            " ".join(d.xpath('.//div[@class="body"]//text()')).replace("\n", "").strip()
        )
        phones = (
            " ".join(d.xpath('.//div[@class="body"]//text()')).replace("\n", "").strip()
        )
        if ad.find("Phone") != -1:
            ad = (
                ad.split("Phone")[0]
                .replace("Ave,", "Ave")
                .replace("St,", "St")
                .replace("Daly City", "Daly_City")
                .replace("Santa Clara", "Santa_Clara")
                .replace("San Mateo", "San_Mateo")
                .replace("San Francisco", "San_Francisco")
            )
        street_address = " ".join(ad.split(",")[0].split()[:-1])
        phone = "<MISSING>"
        if phones.find("Phone") != -1:
            phone = phones.split("Phone:")[1].split("Order")[0].strip()
        state = ad.split(",")[1].split()[0]
        postal = ad.split(",")[1].split()[1]
        country_code = "US"
        city = ad.split(",")[0].split()[-1].replace("_", " ").strip()
        store_number = "<MISSING>"
        map_link = "".join(d.xpath(".//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        if location_name.find("CURRENTLY CLOSED") != -1:
            hours_of_operation = "CURRENTLY CLOSED"

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
