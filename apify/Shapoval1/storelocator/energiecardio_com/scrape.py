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

    locator_domain = "https://www.energiecardio.com"
    api_url = "https://www.energiecardio.com/umbraco/Surface/AjaxSurface/GetFilteredCenters?culture=en&centerTypeId=&isInitialLoad=true&courseId=&originLatitude=&originLongitude="
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js["centers"]:

        page_url = f"{locator_domain}{j.get('centerUrl')}"

        location_name = j.get("name")
        location_type = "GYM"
        street_address = j.get("address")
        phone = j.get("phoneNumber")
        state = j.get("province")
        postal = j.get("postalCode")
        country_code = "CA"
        city = j.get("city")
        store_number = "<MISSING>"
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = tree.xpath(
            '//div[@class="col-sm-6 col-md-6"]/div[@class="openHours"]/div/div//text()'
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation)

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
