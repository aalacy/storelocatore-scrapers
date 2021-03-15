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
    locator_domain = "http://levelsbarbershop.com"
    page_url = "http://levelsbarbershop.com/locations.html"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    block = tree.xpath(
        "//div[.//em[contains(text(), 'Ph')]] | //div[.//span[contains(text(), 'Ph')]]"
    )
    for b in block:

        ad = " ".join(
            b.xpath(
                './/*[contains(text(), "Street")]//text() | .//*[contains(text(), "Avenue")]//text()'
            )
        ).replace("\n", "")
        street_address = ad.split(",")[0].strip()
        if ad.find("125") != -1:
            street_address = ad.split("Harlem")[0]
        street_address = street_address.replace("NY", "")
        phone = (
            "".join(
                b.xpath(
                    ".//em[contains(text(), 'Ph')]/text() | .//span[contains(text(), 'Ph')]/text()"
                )
            )
            .replace("\n", "")
            .split("Ph:")[1]
            .strip()
        )
        city = "<MISSING>"
        if ad.find("Street") != -1:
            city = ad.split("Street")[1].split(",")[0].replace(",", "").strip()
        if ad.find("915") != -1:
            city = ad.split("Street")[1].split(",")[1].replace(",", "").strip()
        if ad.find("2032") != -1:
            city = ad.split(",")[-1].strip()
        state = ad.split(",")[-1].strip()
        location_name = "<MISSING>"
        if ad.find("425") != -1:
            location_name = "125th street location"
        if ad.find("Lexington") != -1:
            location_name = "Lexington Location"
        if ad.find("Fulton") != -1:
            location_name = "brooklyn location"
        if ad.find("115th") != -1:
            location_name = "115th street location"
        country_code = "US"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        postal = "<MISSING>"
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
