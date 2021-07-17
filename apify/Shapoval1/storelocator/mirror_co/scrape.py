import csv
import json
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
    locator_domain = "https://www.mirror.co"
    page_url = "https://www.mirror.co/showroom"
    session = SgRequests()

    r = session.get(page_url)

    tree = html.fromstring(r.text)
    block = "".join(tree.xpath("//@data-nodes")).replace("/n", "").strip()
    block = block.split('"more_locations":')[1].split(',"locations_filter"')[0]

    js = json.loads(block)

    for j in js:

        ad = "".join(j.get("location")).split("\r\n")
        street_address = (
            " ".join(ad[:-1])
            .replace("Northpark", "")
            .replace("Soho Broadway", "")
            .replace("Waterside Shops", "")
            .replace("Georgetown", "")
            .replace(",", "")
            .strip()
            or "<MISSING>"
        )

        adr = (
            "".join(ad[-1])
            .replace("Minneapolis, MN, US", "Minneapolis, MN")
            .replace("United States", "")
            .strip()
        )
        city = adr.split(",")[0] or "<MISSING>"
        if city.find("900B") != -1:
            city = city.replace("900B", "").strip()
            street_address = street_address + " " + "900B"
        postal = adr.split(",")[1].split()[-1].strip() or "<MISSING>"
        state = adr.split(",")[1].split()[0].strip() or "<MISSING>"
        if "323 Oakway Rd" in "".join(ad) or "17 Hillsdale Mall" in "".join(ad):
            street_address = "".join(ad[0]).split(",")[0].strip()
            city = "".join(ad[0]).split(",")[1].strip()
            state = "".join(ad[0]).split(",")[2].split()[0].strip()
            postal = "".join(ad[0]).split(",")[2].split()[1].strip()
        country_code = j.get("country") or "US"
        store_number = "<MISSING>"
        location_name = j.get("title")
        phone = j.get("phone") or "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            "".join(j.get("hours")).replace("\n", "").replace("\r", " ").strip()
        )
        if hours_of_operation.find("BY") != -1:
            hours_of_operation = hours_of_operation.split("ONLY")[1].strip()
        if hours_of_operation.find("See") != -1:
            hours_of_operation = "<MISSING>"
        if hours_of_operation.find("COMING") != -1:
            hours_of_operation = "Coming Soon"

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
