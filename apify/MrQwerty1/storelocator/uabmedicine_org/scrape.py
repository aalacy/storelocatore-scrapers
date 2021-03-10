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


def get_coords_from_page(page_url):
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//div[@class='service-links']//a[contains(@href, 'map')]/@href")
    )

    return get_coords(text)


def get_coords(map_url):
    try:
        if map_url.find("ll=") != -1:
            latitude = map_url.split("ll=")[1].split(",")[0]
            longitude = map_url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = map_url.split("@")[1].split(",")[0]
            longitude = map_url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_addr(line):
    street_address = line[0]
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    return street_address, city, state, postal


def get_line(page_url):
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='service-links']//address/a/text()")


def fetch_data():
    out = []
    api_url = "https://www.uabmedicine.org/locations"
    locator_domain = "https://www.uabmedicine.org/"
    country_code = "US"
    store_number = "<MISSING>"
    hours_of_operation = "<MISSING>"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    groups = tree.xpath("//div[@class='panel-group']")[1:]
    for g in groups:
        containers = g.xpath(".//div[contains(@class, 'col-md-')]")
        location_type = "".join(
            g.xpath(".//a[@data-toggle='collapse' and not(@class='btn')]/text()")
        ).strip()
        for c in containers:
            _class = "".join(c.xpath("./@class")).strip()
            if _class == "col-md-8" or _class == "col-md-12":
                continue

            location_name = " ".join(
                "".join(c.xpath(".//h2//text()|./strong/text()")).split()
            )
            if not location_name or location_name.find("eMedicine") != -1:
                continue

            slug = "".join(c.xpath(".//h2/a/@href"))
            if slug.startswith("http") and slug.find("uabmedicine.org") != -1:
                page_url = slug
            elif slug.startswith("/"):
                page_url = f"https://www.uabmedicine.org{slug}"
            else:
                page_url = "<MISSING>"

            if _class == "col-sm-6 col-md-6" and len(c.xpath(".//address")) == 2:
                location_name = location_name.split("(")[0].strip()
                line = get_line(page_url)
                line = list(
                    filter(
                        None,
                        [l.replace("\t", "").replace("\n", "").strip() for l in line],
                    )
                )
                street_address, city, state, postal = get_addr(line)
                phone = c.xpath(".//address[1]/a[contains(@href, 'tel:')]/@href")[
                    0
                ].replace("tel:", "")
                text = "".join(c.xpath(".//address[1]/a[contains(@href, 'map')]/@href"))
                latitude, longitude = get_coords(text)
                if (
                    latitude == "<MISSING>" and longitude == "<MISSING>"
                ) and page_url != "<MISSING>":
                    latitude, longitude = get_coords_from_page(page_url)
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

                location_name = "".join(
                    c.xpath("./a[contains(@href, 'location')]/text()")
                ).strip()
                slug = "".join(c.xpath("./a[contains(@href, 'location')]/@href"))
                page_url = f"https://www.uabmedicine.org{slug}"
                line = c.xpath(".//address[2]/a[contains(@href, 'map')]/text()")
                line = list(
                    filter(
                        None,
                        [l.replace("\t", "").replace("\n", "").strip() for l in line],
                    )
                )
                street_address, city, state, postal = get_addr(line)
                phone = c.xpath(".//address[2]/a[contains(@href, 'tel:')]/@href")[
                    0
                ].replace("tel:", "")
                text = "".join(c.xpath(".//address[2]/a[contains(@href, 'map')]/@href"))
                latitude, longitude = get_coords(text)
                if (
                    latitude == "<MISSING>" and longitude == "<MISSING>"
                ) and page_url != "<MISSING>":
                    latitude, longitude = get_coords_from_page(page_url)
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
            else:
                if _class == "col-sm-6 col-md-6":
                    line = get_line(page_url)
                else:
                    line = c.xpath(".//a[contains(@href, 'map')]/text()")
                line = list(
                    filter(
                        None,
                        [l.replace("\t", "").replace("\n", "").strip() for l in line],
                    )
                )
                street_address, city, state, postal = get_addr(line)
                phone = c.xpath(".//a[contains(@href, 'tel:')]/@href")[0].replace(
                    "tel:", ""
                )
                text = "".join(c.xpath(".//a[contains(@href, 'map')]/@href"))
                latitude, longitude = get_coords(text)
                if (
                    latitude == "<MISSING>" and longitude == "<MISSING>"
                ) and page_url != "<MISSING>":
                    latitude, longitude = get_coords_from_page(page_url)

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
