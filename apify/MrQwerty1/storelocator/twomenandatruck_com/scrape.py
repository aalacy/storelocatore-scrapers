import csv

from concurrent import futures
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


def get_hours(_id):
    _tmp = []
    session = SgRequests()
    r = session.get(
        f"https://twomenandatruck.com/location-block/{_id}/tmt_location_banner_hours"
    )
    source = r.json()["html"] or "<html></html>"
    tree = html.fromstring(source)
    divs = tree.xpath("//div[@class='office-hours__item']")

    for d in divs:
        day = "".join(d.xpath("./span[1]//text()")).strip()
        time = "".join(d.xpath("./span[2]//text()")).strip()
        _tmp.append(f"{day} {time}")

    return ";".join(_tmp) or "<MISSING>"


def fetch_data():
    out = []
    hours = dict()
    ids = []
    locator_domain = "https://twomenandatruck.com/"
    api_url = "https://twomenandatruck.com/feed/locations"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["locations"]

    for j in js:
        ids.append(j.get("location_id"))

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_hours, _id): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            _id = future_to_url[future]
            hours[_id] = row

    for j in js:
        street_address = (
            f"{j.get('address_street')} {j.get('address_premise') or ''}".strip()
            or "<MISSING>"
        )
        city = j.get("address_city") or "<MISSING>"
        state = j.get("address_state_province") or "<MISSING>"
        postal = j.get("address_postal_code") or "<MISSING>"
        country_code = j.get("address_country") or "<MISSING>"
        store_number = j.get("location_id") or "<MISSING>"
        page_url = j.get("web_landing_page")
        location_name = f"Movers in {j.get('location_name')}, {state}"
        phone = j.get("phone_office") or "<MISSING>"
        latitude = j.get("coordinates_latitude") or "<MISSING>"
        longitude = j.get("coordinates_longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = hours.get(store_number)

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
