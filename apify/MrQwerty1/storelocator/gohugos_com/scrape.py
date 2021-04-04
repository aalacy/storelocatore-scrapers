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


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_additional(page_url):
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    phone = tree.xpath(
        "//p[contains(text(), '-') and not(./*)]/text()|//p[./strong[contains(text(), 'Phone')]]/text()"
    )[0].strip()
    text = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)
    hours = tree.xpath(
        "//p[following-sibling::p[1][text()='Hours:']]/following-sibling::p/text()|//p[following-sibling::p[1][./*[text()='Hours:']]]/following-sibling::p/text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hoo = (
        " ".join(hours)
        .replace("Hours:", "")
        .replace("pm", "pm;")
        .replace("12pm;", "12pm")
        .strip()
        or "<MISSING>"
    )
    if "(" in hoo:
        hoo = hoo.split("(")[0].strip()

    return phone, latitude, longitude, hoo


def fetch_data():
    out = []
    locator_domain = "https://www.gohugos.com/"
    api_url = "https://www.gohugos.com/store-locations/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    sections = tree.xpath("//div[contains(@id, 'av_section_')]")

    for section in sections:
        location_type = (
            "".join(
                section.xpath(".//h2[contains(@class, 'av-special-heading')]/text()")
            )
            .replace(" Locations", "")
            .replace("  ", " & ")
        )
        articles = section.xpath(".//article")

        for a in articles:
            location_name = "".join(
                a.xpath(".//h3[@itemprop='headline']/text()")
            ).strip()
            page_url = "".join(a.xpath(".//a[text()='View Details']/@href")) or api_url

            line = a.xpath(
                ".//div[contains(@class,'iconbox_content_container')]/p[1]/text()"
            )
            line = list(filter(None, [l.strip() for l in line]))

            street_address = line[0]
            line = line[-1]
            city = line.split(",")[0].strip()
            line = line.split(",")[1].strip()
            state = line.split()[0]
            postal = line.split()[-1]
            country_code = "US"
            store_number = "<MISSING>"
            if page_url == api_url:
                phone = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                hours_of_operation = "<MISSING>"
            else:
                phone, latitude, longitude, hours_of_operation = get_additional(
                    page_url
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
