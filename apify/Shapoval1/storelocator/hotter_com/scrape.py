import csv
import json
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
    locator_domain = "https://www.hotter.com"
    api_url = "https://www.hotter.com/shoe-shops/"

    session = SgRequests()
    r = session.get(api_url)
    block1 = r.text.split("var stores = [")[1].split("]")[0]
    block = "[" + block1 + "]"
    js = json.loads(block)
    for j in js:
        ad = j.get("custom_data")
        street_address = (
            f"{ad.get('address_1')} {ad.get('address_2')} {ad.get('address_3')}"
        )
        city = ad.get("city")
        postal = "".join(ad.get("postcode")).split("(")[0].strip()
        state = "".join(ad.get("region"))
        phone = "".join(ad.get("phone"))

        country_code = "".join(ad.get("country"))
        store_number = "<MISSING>"
        location_name = "".join(j.get("post_name"))
        latitude = ad.get("location").get("lat")
        longitude = ad.get("location").get("lng")
        location_type = "<MISSING>"
        page_url = j.get("permalink")
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
            days = d
            open = ad.get(f"{d}_opening_times").get(f"{d}_open")
            close = ad.get(f"{d}_opening_times").get(f"{d}_close")
            line = f"{days} {open} - {close}"
            if (
                ad.get(f"{d}_opening_times").get(f"{d}_status") == "Closed"
                and open == ""
                and close == ""
            ):
                open = "Closed"
                line = f"{d} {open}"
            tmp.append(line)
        hours_of_operation = ";".join(tmp)
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
