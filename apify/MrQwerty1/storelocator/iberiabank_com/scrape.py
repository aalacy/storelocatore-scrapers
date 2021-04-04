import csv

from concurrent import futures
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


def generate_links():
    session = SgRequests()
    r = session.get("https://locations.iberiabank.com/index.json")
    js = r.json()["directoryHierarchy"]

    urls = list(get_urls(js))

    return urls


def get_urls(states):
    for state in states.values():
        children = state["children"]
        if children is None:
            yield f"https://locations.iberiabank.com/{state['url']}.json"
        else:
            yield from get_urls(children)


def get_data(url):
    session = SgRequests()
    r = session.get(url)
    j = r.json()["profile"]

    locator_domain = "https://locations.iberiabank.com/"
    page_url = url.replace(".json", "")
    location_name = (
        f"{j.get('name')} {j.get('geomodifier') or ''}".strip() or "<MISSING>"
    )

    a = j.get("address", {}) or {}
    street_address = f"{a.get('line1')} {a.get('line2') or ''}".strip() or "<MISSING>"
    city = a.get("city") or "<MISSING>"
    state = a.get("region") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = a.get("countryCode") or "<MISSING>"
    store_number = "<MISSING>"
    phone = j.get("mainPhone").get("display") if j.get("mainPhone") else "<MISSING>"
    loc = j.get("yextDisplayCoordinate", {}) or {}
    latitude = loc.get("lat") or "<MISSING>"
    longitude = loc.get("long") or "<MISSING>"
    location_type = "<MISSING>"
    days = j.get("hours", {}).get("normalHours") or []

    _tmp = []
    for d in days:
        day = d.get("day")[:3].capitalize()
        try:
            interval = d.get("intervals")[0]
            start = str(interval.get("start"))
            if start == "0":
                _tmp.append("24 hours")
                break
            end = str(interval.get("end"))

            # normalize 9:30 -> 09:30
            if len(start) == 3:
                start = f"0{start}"

            if len(end) == 3:
                end = f"0{end}"

            line = f"{day}  {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"
        except IndexError:
            line = f"{day}  Closed"

        _tmp.append(line)

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if (
        hours_of_operation.count("Closed") == 7
        or location_name.lower().find("closed") != -1
    ):
        hours_of_operation = "Closed"

    if location_name.lower().find(":") != -1:
        location_name = location_name.split(":")[0].strip()

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
    ids = generate_links()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, _id): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
