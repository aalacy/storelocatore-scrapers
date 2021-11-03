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

    locator_domain = "https://www.holtrenfrew.com/"
    api_url = "https://www.holtrenfrew.com/en/stores?location=bloorstreet"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//script[contains(text(), "20-006-individual-store")]/text()')

    for d in div:
        slug = "".join(d).split("id:")[1].split(",")[0].replace("`", "").strip()
        page_url = f"https://www.holtrenfrew.com/en/stores?location={slug}"
        location_name = (
            "".join(d).split("name:")[1].split(",")[0].replace("`", "").strip()
        )
        location_type = "<MISSING>"
        ad = "".join(d).split("address:")[1].split("`,")[0].replace("`", "").strip()
        street_address = ad.split("<br>")[0].strip()
        adr = ad.split("<br>")[1].strip()
        phone = (
            "".join(d).split("phoneNumber:")[1].split(",")[0].replace("`", "").strip()
        )
        state = adr.split(",")[1].split()[0].strip()
        postal = " ".join(adr.split(",")[1].split()[1:]).strip()
        country_code = "CA"
        city = adr.split(",")[0].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours = "".join(d).split("/*html*/")[1].split(",")[0].replace("`", "").strip()
        h = html.fromstring(hours)
        hours_of_operation = (
            " ".join(h.xpath("//div/span/text()")).replace("\n", "").strip()
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
