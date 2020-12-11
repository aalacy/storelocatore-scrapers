import csv

from concurrent import futures
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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


def generate_links():
    r = session.get("https://locations.fazolis.com/index.json")
    js = r.json()["directoryHierarchy"]
    urls = list(get_urls(js))
    return urls


def get_urls(states):
    for state in states.values():
        children = state["children"]
        if children is None:
            yield f"https://locations.fazolis.com/{state['url']}"
        else:
            yield from get_urls(children)


def get_data(page_url):
    locator_domain = "https://fazolis.com/"
    r = session.get(page_url.replace(".html", ".json"))
    j = r.json()

    street_address = (
        f"{j.get('address1')} {j.get('address2') or ''}".strip() or "<MISSING>"
    )
    city = j.get("city") or "<MISSING>"
    location_name = f"{j.get('name')} {city}" or "<MISSING>"
    if location_name.lower().find("coming") != -1:
        return
    state = j.get("state") or "<MISSING>"
    postal = j.get("postalCode") or "<MISSING>"
    country_code = j.get("country") or "<MISSING>"
    store_number = j.get("corporateCode") or "<MISSING>"
    phone = j.get("phone") or "<MISSING>"
    latitude = j.get("latitude") or "<MISSING>"
    longitude = j.get("longitude") or "<MISSING>"
    location_type = "<MISSING>"
    days = j.get("hours", {}).get("days") or "<MISSING>"
    if days == "<MISSING>":
        hours_of_operation = days
    else:
        _tmp = []
        for d in days:
            day = d.get("day")[:3].capitalize()
            try:
                interval = d.get("intervals")[0]
                start = str(interval.get("start"))
                end = str(interval.get("end"))
                # normalize 9:30 -> 09:30
                if len(start) == 3:
                    start = f"0{start}"
                line = f"{day}  {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"
            except IndexError:
                line = f"{day}  Closed"
            _tmp.append(line)
        hours_of_operation = ";".join(_tmp)

        # skip closed locations
        if hours_of_operation.count("Closed") == 7:
            return

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
    return row


def fetch_data():
    out = []
    urls = generate_links()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    session = SgRequests()
    scrape()
