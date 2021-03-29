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


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def fetch_data():
    out = []
    locator_domain = "https://www.wgrfurniture.com/"
    page_url = "https://www.wgrfurniture.com/locations-hours/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='locationslist-wrap']")

    for _div in divs:
        _tmp = []
        tr = _div.xpath("./preceding-sibling::table[1]//tr")
        for t in tr:
            day = "".join(t.xpath("./td[1]/text()")).strip()
            time = "".join(t.xpath("./td[2]/text()")).strip()
            _tmp.append(f"{day} {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        for d in _div.xpath(".//div[@class='accordion-wrap']"):
            location_name = (
                "".join(
                    d.xpath(".//div[@class='accordion-title clearfix']/p/text()")
                ).strip()
                or "<MISSING>"
            )
            line = d.xpath(".//div[@class='accordion-content']/p/text()")
            line = list(filter(None, [l.strip() for l in line]))

            phone = line.pop()
            street_address = line[0]
            line = line[1]
            city = line.split(",")[0].strip()
            line = line.split(",")[1].strip()
            state = line.split()[0]
            postal = line.split()[1]
            country_code = "US"
            store_number = "<MISSING>"
            text = "".join(d.xpath(".//a/@href"))
            latitude, longitude = get_coords_from_google_url(text)
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
