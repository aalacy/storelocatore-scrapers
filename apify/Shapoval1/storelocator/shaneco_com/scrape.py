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
    locator_domain = "https://www.shaneco.com"
    api_url = "https://www.shaneco.com/jewelry-store-finder/storeposition"
    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["infoWindowContent"]
    for j in js:
        street_address = "".join(j.get("addressLineOne")) or "<MISSING>"
        line = j.get("addressLineTwo")
        city = "".join(line).split(",")[0] or "<MISSING>"
        line = "".join(line).split(",")[1].strip()
        state = "".join(line).split()[0].strip()
        postal = "".join(line).split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        slug = "".join(j.get("region"))
        store_id = "".join(j.get("storeId"))
        page_url = f"https://www.shaneco.com/jewelry-stores/{slug}/{store_id}"
        location_name = "".join(j.get("place"))
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        hours = tree.xpath('//div[@class="store-item__workhours_hold"]/p/text()')
        hours_of_operation = ":".join(hours)
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
