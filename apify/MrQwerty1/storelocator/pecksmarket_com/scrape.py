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
    locator_domain = "http://pecksmarket.com/"
    page_url = "http://pecksmarket.shoptocook.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
    }

    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='entry-content']/h2")

    for d in divs:
        location_name = "".join(d.xpath("./text()")).strip()
        line = d.xpath("./following-sibling::p[1]/text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = ", ".join(line[:-2])
        line = line[-2].replace(",", "")
        postal = line.split()[-1]
        state = line.split()[-2]
        city = line.replace(postal, "").replace(state, "").strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath("./following-sibling::p[1]/strong/text()")).strip()
            or "<MISSING>"
        )

        text = "".join(d.xpath("./following-sibling::p[3]/a/@href"))
        latitude, longitude = get_coords_from_google_url(text)
        location_type = "<MISSING>"

        hours = " ".join(" ".join(d.xpath("./following-sibling::p[2]/text()")).split())
        hours_of_operation = hours.replace("pm", "pm;").replace(",", "") or "<MISSING>"

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
