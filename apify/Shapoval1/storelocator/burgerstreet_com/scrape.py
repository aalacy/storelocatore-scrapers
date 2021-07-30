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
    locator_domain = "https://www.burgerstreet.com"
    api_url = "https://www.burgerstreet.com/index.php?option=com_storelocator&view=map&format=raw&searchall=1&Itemid=470&catid=-1&tagid=-1&featstate=0"

    session = SgRequests()
    r = session.get(api_url)

    tree = html.fromstring(r.content)
    block = tree.xpath("//markers/marker")

    for b in block:

        page_url = "https://www.burgerstreet.com/index.php/locations"

        location_name = "".join(b.xpath(".//name/text()"))

        street_address = "".join(b.xpath(".//address/text()"))
        city = "<MISSING>"
        state = "<MISSING>"
        postal = (
            "".join(b.xpath('.//*[contains(text(), "Zip")]/text()'))
            .replace("Zip :", "")
            .strip()
        )
        if postal.find("US") != -1:
            postal = "<MISSING>"
        phone = (
            "".join(b.xpath('.//*[contains(text(), "Phone")]/text()'))
            .replace("Phone :", "")
            .strip()
        )

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        latitude = "".join(b.xpath(".//lat/text()"))
        longitude = "".join(b.xpath(".//lng/text()"))

        hours_of_operation = (
            " ".join(
                b.xpath(
                    './/*[contains(text(), "pm")]/text() | .//p[contains(text(), "Temporarily")]/text() | .//p[contains(text(), "Closed on")]/text()'
                )
            )
            .replace("Time :", "")
            .replace("&", "-")
            .replace("SUB", "SAT")
            .replace("am", " am")
            .replace("pm", " pm")
            .replace("to", "-")
            .replace("</p", "")
            .strip()
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
