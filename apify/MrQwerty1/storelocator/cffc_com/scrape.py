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


def get_coords():
    coords = dict()
    session = SgRequests()
    r = session.get(
        "https://www.google.com/maps/d/u/0/kml?mid=1TsdMMRMjHESTZ6HL0vJ3amcLp-o&forcekml=1"
    )
    text = str(r.content).replace("<![CDATA[", "").replace("]]", "").replace(">>", ">")
    tree = html.fromstring(text)
    markers = tree.xpath("//placemark")
    for m in markers:
        name = "".join(m.xpath(".//name/text()"))
        if not name:
            continue
        lng, lat = (
            "".join(m.xpath(".//coordinates/text()")).replace(",0", "").split(",")
        )
        coords[name] = (
            lat.replace("\\", "").replace("n", "").strip(),
            lng.replace("\\", "").replace("n", "").strip(),
        )

    return coords


def fetch_data():
    out = []
    coords = get_coords()
    locator_domain = "https://cffc.com/"
    page_url = "https://cffc.com/Locations.aspx"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    ids = tree.xpath("//a[text()='Hours']/@href")

    for _id in ids:
        i = _id.replace("#", "")
        d = tree.xpath(f"//table[@id='{i}']")[0]
        location_name = "".join(d.xpath(".//h2/text()")).strip()

        line = "".join(d.xpath(".//h2/following-sibling::p/text()")).split("|")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()"))
            .replace("|", "")
            .strip()
            or "<MISSING>"
        )

        latitude = "<MISSING>"
        longitude = "<MISSING>"

        for k, v in coords.items():
            if location_name.lower() in k.lower():
                latitude, longitude = v
                break

        if latitude == "<MISSING>":
            text = "".join(d.xpath(".//a[text()='Map It']/@href"))
            latitude, longitude = get_coords_from_google_url(text)

        location_type = "<MISSING>"
        hours_of_operation = (
            ";".join(
                d.xpath(
                    ".//strong[contains(text(), 'Lobby')]/following-sibling::text()"
                )
            )
            or "<MISSING>"
        )

        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                ";".join(
                    d.xpath(
                        ".//strong[contains(text(), 'Office')]/following-sibling::text()"
                    )
                )
                or "<MISSING>"
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
