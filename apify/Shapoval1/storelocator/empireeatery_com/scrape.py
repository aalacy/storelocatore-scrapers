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

    locator_domain = "https://www.empireeatery.com"
    page_url = "https://www.empireeatery.com/find-us"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//h2[.//span[contains(text(), "(")]]')

    for d in div:

        location_type = "<MISSING>"
        ad = "".join(d.xpath(".//preceding-sibling::h2[1]//text()"))
        street_address = (
            "".join(d.xpath(".//preceding-sibling::h2[2]//text()"))
            .replace("\n", "")
            .strip()
        )
        phone = "".join(d.xpath(".//text()"))
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_name = "<MISSING>"
        hours_of_operation = "<MISSING>"
        if city == "WEEDSPORT":
            location_name = "Weedsport"
            hours_of_operation = "24 Hours"
        if city == "PORT BYRON":
            location_name = "PORT BYRON"
            hours_of_operation = "MON-SAT 5AM -11PM SUNDAY 6AM -11PM"
        if city == "FULTON":
            location_name = "GRANBY CENTER"
            hours_of_operation = "MON-SAT 5 AM - 11PM SUNDAY 6AM -10PM"
        if city == "GENOA":
            location_name = "GENOA"
            hours_of_operation = "MON-THURS 5AM-9PM FRI- SAT 5AM-10PM SUN 6AM-9PM"
        city = city.capitalize()
        location_name = location_name.capitalize()
        hours_of_operation = hours_of_operation.lower()
        street_address = street_address.capitalize()

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
