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

    locator_domain = "https://www.shiproadrunnerfreight.com/"
    page_url = "https://www.shiproadrunnerfreight.com/about-us/our-network/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="modal-content"]')
    for d in div:

        location_name = "".join(d.xpath(".//h3/text()"))
        ad = d.xpath(".//p/text()")
        ad = list(filter(None, [a.strip() for a in ad]))

        location_type = "<MISSING>"
        street_address = "".join(ad[0]).strip()
        adr = "".join(ad[1]).replace("Farmingdale", "Farmingdale,")

        state = adr.split(",")[1].split()[0].strip()
        postal = adr.split(",")[1].split()[1].strip()
        country_code = "US"
        city = adr.split(",")[0].strip()

        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        phone = "".join(ad[-1]).strip()
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
