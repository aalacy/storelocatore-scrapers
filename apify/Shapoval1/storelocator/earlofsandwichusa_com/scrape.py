import csv
from lxml import html
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
    r = session.get("https://locations.earlofsandwichusa.com/index.json")
    js = r.json()["directoryHierarchy"]

    urls = list(get_urls(js))
    urrls = []
    for i in urls:
        if "virtual" in i:
            continue
        urrls.append(i)
    urrls.append("https://locations.earlofsandwichusa.com/us/ca/valley-center.json")
    urrls.append("https://locations.earlofsandwichusa.com/us/fl/lake-worth.json")
    urrls.append("https://locations.earlofsandwichusa.com/us/fl/miami.json")
    urrls.append("https://locations.earlofsandwichusa.com/us/fl/okeechobee.json")
    urrls.append("https://locations.earlofsandwichusa.com/us/fl/port-st--lucie.json")
    urrls.append("https://locations.earlofsandwichusa.com/us/nj/newark.json")
    urrls.append("https://locations.earlofsandwichusa.com/us/nc/cherokee.json")
    urrls.append("https://locations.earlofsandwichusa.com/us/nc/murphy.json")
    urrls.append("https://locations.earlofsandwichusa.com/us/pa/philadelphia.json")
    urrls.append("https://locations.earlofsandwichusa.com/us/md/northeast.json")

    return urrls


def get_urls(states):
    for state in states.values():
        children = state["children"]
        if children is None:
            yield f"https://locations.earlofsandwichusa.com/{state['url']}.json"
        else:
            yield from get_urls(children)


def get_data(url):
    session = SgRequests()
    r = session.get(url)
    j = r.json()
    if "directoryHierarchy" in j:
        j = r.json()["keys"][0]["loc"]
    locator_domain = "https://www.bloomingdales.com"
    page_url = url.replace(".json", "")
    if page_url.count("/") == 5:
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        page_url = "".join(tree.xpath('//a[text()="Visit Location"]/@href'))

    location_name = j.get("name") or "<MISSING>"

    street_address = (
        f"{j.get('address1')} {j.get('address2') or ''}".strip() or "<MISSING>"
    )
    if street_address.find("Boca Town Center Mall") != -1:
        street_address = street_address.replace("Boca Town Center Mall", "").strip()
    if street_address.find("Boston Common") != -1:
        street_address = street_address.replace("Boston Common", "").strip()
    if street_address.find("International Mall Food Court") != -1:
        street_address = street_address.replace(
            "International Mall Food Court", ""
        ).strip()
    if street_address.find("Terminal D, Philadelphia International Airport") != -1:
        street_address = street_address.replace(
            "Terminal D, Philadelphia International Airport", ""
        ).strip()
    city = j.get("city") or "<MISSING>"
    state = j.get("state") or "<MISSING>"
    postal = j.get("postalCode") or "<MISSING>"
    country_code = j.get("country") or "<MISSING>"
    if country_code == "FR":
        return
    store_number = "<MISSING>"

    phone = j.get("phone") or "<MISSING>"
    latitude = j.get("latitude") or "<MISSING>"
    longitude = j.get("longitude") or "<MISSING>"
    location_type = "<MISSING>"
    days = j.get("hours", {}).get("days") or []

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
