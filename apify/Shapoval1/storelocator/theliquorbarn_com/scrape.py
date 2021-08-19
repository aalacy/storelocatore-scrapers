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

    locator_domain = "https://www.theliquorbarn.com"
    api_url = "https://www.theliquorbarn.com/pages/locations.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//tr[./td/p[@align="left"]]/td')

    for d in div:
        page_url = "https://www.theliquorbarn.com/pages/locations.html"
        ad = d.xpath(".//text()")
        ad = list(filter(None, [a.strip() for a in ad]))
        if "NOW OPEN!" in ad:
            ad.pop(0)
        location_name = "".join(ad[0]).replace(":", "").strip()
        adr = "".join(ad[2]).strip()
        location_type = "<MISSING>"
        street_address = adr.split(",")[0].strip()
        state = adr.split(",")[2].split()[0].strip()
        postal = adr.split(",")[2].split()[1].strip()
        country_code = "US"
        city = adr.split(",")[1].strip()
        store_number = "<MISSING>"
        map_link = "".join(d.xpath(".//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = "".join(ad[5]).replace("Direct line:", "").strip()
        hours_of_operation = "".join(ad[4]).strip()
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
