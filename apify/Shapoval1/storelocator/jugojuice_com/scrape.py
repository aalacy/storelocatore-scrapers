import csv
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgpostal import International_Parser, parse_address


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

    locator_domain = "https://jugojuice.com/"
    api_url = "https://jugojuice.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=en&t=1626429161801.xml"

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    div = r.text.split("<item>")

    for d in div[1:]:

        page_url = (
            d.split("<exturl>")[1].split("</exturl>")[0].strip()
            or "https://jugojuice.com/locations/"
        )
        ad = (
            d.split("<address>")[1]
            .split("</address>")[0]
            .replace("#44;", ",")
            .replace("&amp;", " ")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        if street_address == "15":
            street_address = ad.split(",")[0].strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        city = a.city or "<MISSING>"
        store_number = "<MISSING>"
        location_name = (
            d.split("<location>")[1]
            .split("</location>")[0]
            .replace("&#39;", "`")
            .replace("&amp;", "&")
            .replace("&#39;", "`")
            .strip()
        )

        latitude = d.split("<latitude>")[1].split("</latitude>")[0].strip()
        longitude = d.split("<longitude>")[1].split("</longitude>")[0].strip()
        if latitude.find("°") != -1:
            latitude = (
                latitude.replace(".", "")
                .replace("° ", ".")
                .replace("&#39; ", "")
                .strip()
            )
            longitude = (
                longitude.replace(".", "")
                .replace("° ", ".")
                .replace("&#39; ", "")
                .strip()
            )
        country_code = "CA"
        location_type = "Jugo Juice"
        phone = d.split("<telephone>")[1].split("</telephone>")[0].strip()
        hours_of_operation = (
            d.split("<operatingHours>")[1]
            .split("</operatingHours>")[0]
            .replace("\n", "")
            or "<MISSING>"
        )
        if hours_of_operation != "<MISSING>":
            a = html.fromstring(hours_of_operation)
            hours_of_operation = (
                "".join(a.xpath("//*//text()")).replace("\n", "").strip()
            )
            a = html.fromstring(hours_of_operation)
            hours_of_operation = a.xpath("//*//text()")
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = " ".join(hours_of_operation)
        hours_of_operation = (
            hours_of_operation.replace(" <br> ", " ")
            .replace("​​", "")
            .replace("​", "")
            .replace("<br>", "")
            .strip()
        )
        if hours_of_operation.find("*") != -1:
            hours_of_operation = hours_of_operation.split("*")[0].strip()
        if hours_of_operation.find("(") != -1:
            hours_of_operation = hours_of_operation.split("(")[0].strip()
        if "Temporarily Closed" in location_name:
            location_type = "Temporarily Closed"
        if "temporarily closed" in location_name:
            location_type = "Temporarily Closed"

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
