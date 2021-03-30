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
    locator_domain = "https://www.qualityfoods.com/"
    page_url = "https://www.qualityfoods.com/about-qf/location-hours"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='sfContentBlock']")[:-1]

    for d in divs:
        location_name = " ".join("".join(d.xpath("./h1/text()|./h2/text()")).split())
        line = d.xpath("./text()|./p//text()")
        line = list(filter(None, [l.strip() for l in line]))

        if not line[1][0].isdigit():
            street_address = line[0]
            city = line[1].split(",")[0].strip()
            state = line[1].split(",")[1].strip()
            phone = line[2].replace("/", "").strip()
        else:
            phone = line[1].replace("/", "").strip()
            state = line[0].split(",")[1].strip()
            line = line[0].split(",")[0].strip()
            city = line.split()[-1]
            street_address = line.replace(city, "").strip()

        postal = "<MISSING>"
        country_code = "CA"
        store_number = "<MISSING>"
        if street_address.startswith("#"):
            store_number = street_address.split(" - ")[0].replace("#", "")
            street_address = street_address.split(" - ")[1].strip()

        text = "".join(d.xpath("./a/@href"))
        if text:
            latitude, longitude = get_coords_from_google_url(text)
        else:
            latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = d.xpath(
            ".//strong[contains(text(), 'Store Hours')]/following-sibling::div[1]/text()|.//strong[contains(text(), 'Store Hours')]/following-sibling::text()"
        )
        hours_of_operation = list(
            filter(None, [h.replace("-", " ").strip() for h in hours_of_operation])
        )
        hours_of_operation = (
            "".join(hours_of_operation).replace("   ", " - ") or "<MISSING>"
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
