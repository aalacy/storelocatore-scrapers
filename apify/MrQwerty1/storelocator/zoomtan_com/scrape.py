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


def get_hours(page_url):
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    hours = tree.xpath("//div[@id='storehrs']//text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    hours = " ".join(";".join(hours).split()) or "<MISSING>"
    phone = (
        "".join(
            tree.xpath("//div[@id='storecontact']//a[contains(@href, 'tel:')]/text()")
        ).strip()
        or "<MISSING>"
    )

    return {"hours": hours, "phone": phone}


def fetch_data():
    out = []
    urls = []
    hours = dict()
    locator_domain = "https://www.zoomtan.com/"
    api_url = "https://www.zoomtan.com/tanning-salon-locations/"

    data = {"doajx": "1", "do": "search_map_initial"}

    session = SgRequests()
    r = session.post(api_url, data=data)
    js = r.json()

    for j in js:
        urls.append(j.get("page_url"))

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_hours, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            url = future_to_url[future]
            _id = url.split("/")[-1]
            hours[_id] = row

    for j in js:
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id")
        page_url = j.get("page_url")
        location_name = f"Zoom Tan UV & Spray Tanning Salon - {city}, {state}"
        phone = hours[store_number]["phone"]
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = hours[store_number]["hours"]
        if "COMING SOON -" in street_address:
            hours_of_operation = "COMING SOON"
            street_address = street_address.replace("COMING SOON -", "").strip()

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
