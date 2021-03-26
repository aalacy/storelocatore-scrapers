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
    locator_domain = "https://www.doggiestylepets.com/"
    page_url = "https://www.doggiestylepets.com/pages/find-a-store"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[contains(@class,'one-half-column')]|//div[@class='rte']")

    for d in divs:
        location_name = (
            "".join(d.xpath("./strong/a/span/text()")).replace("‣", "").strip()
        )
        line = d.xpath("./text()")
        line = list(filter(None, [l.strip() for l in line]))
        if not line:
            continue

        street_address = line[0][:-1]
        phone = line[-1]
        line = line[1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = "<MISSING>"

        text = "".join(d.xpath(".//strong/a/@href"))
        latitude, longitude = get_coords_from_google_url(text)
        location_type = "<MISSING>"

        _tmp = []
        pp = tree.xpath("//h3[text()='Hours']/following-sibling::div[1]/p[./strong]")
        for p in pp:
            day = "".join(p.xpath("./strong/text()")).strip()
            time = "".join(p.xpath("./text()")).strip()
            _tmp.append(f"{day} {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
