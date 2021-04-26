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
    locator_domain = "https://www.juicegeneration.com"
    api_url = "https://www.juicegeneration.com/locations/"

    session = SgRequests()

    r = session.get(api_url)

    tree = html.fromstring(r.text)
    block = "".join(tree.xpath('//script[contains(text(), "locationsJSON")]//text()'))
    block = block.split("locationsJSON = ")[1].split(";")[0]
    js = json.loads(block)
    for j in js.values():

        street_address = f"{j.get('address1')} {j.get('address2')}".strip()
        city = "<MISSING>"
        postal = j.get("zipcode")
        state = "<MISSING>"
        next = " ".join(street_address.split()[4:])
        if street_address.find("630") != -1:
            street_address = " ".join(street_address.split()[:4])

            city = next.split(",")[0]
            state = next.split(",")[1]
        phone = j.get("phone") or "<MISSING>"
        country_code = "<MISSING>"
        store_number = j.get("location_id")
        location_name = j.get("name")
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        url_path = "".join(j.get("url_path"))
        page_url = f"https://www.juicegeneration.com/locations/{url_path}"
        ad = j.get("work_hours")
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        tmp = []
        for d in days:
            days = d.capitalize()
            open = ad.get(f"{d}_work_hours").get("start")
            close = ad.get(f"{d}_work_hours").get("end")
            line = f"{days} {open} - {close}"
            tmp.append(line)
        hours_of_operation = ";".join(tmp) or "<MISSING>"

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
