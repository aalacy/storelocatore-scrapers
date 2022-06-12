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
    locator_domain = "https://earlofsandwichusa.com/"
    page_url = url.replace(".json", "")
    if page_url.count("/") == 5:
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        page_url = "".join(tree.xpath('//a[text()="Visit Location"]/@href'))

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
    if street_address.find("Tom Bradley Terminal") != -1:
        street_address = street_address.replace("Tom Bradley Terminal", "").strip()
    if street_address.find("International Mall") != -1:
        street_address = street_address.replace("International Mall", "").strip()
    if street_address.find("Mile Post 97") != -1:
        street_address = street_address.replace("Mile Post 97", "").strip()
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

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "TE": "Trailers",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    location_name = (
        "".join(tree.xpath('//h1//span[@class="LocationName-geo"]/text()'))
        or "<MISSING>"
    )
    if location_name == "<MISSING>":
        location_name = "".join(tree.xpath("//h1/text()")).replace("\n", "").strip()

    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//h2[@class="c-location-hours-title"]/following-sibling::div[1]/table//tr//td//text()'
            )
        )
        .replace("\n", "")
        .replace("  ", " ")
        .strip()
        or "<MISSING>"
    )
    if hours_of_operation == "<MISSING>":
        hours_of_operation = (
            " ".join(tree.xpath('//div[@id="store_hours"]/p//text()'))
            .replace("\n", "")
            .strip()
        )
    if hours_of_operation.count("Closed") == 7:
        hours_of_operation = "Closed"
    hours_of_operation = hours_of_operation.replace(
        "Closed Closed Closed Closed", "Mon Closed Tue Closed Wed Closed Thu Closed"
    ).replace("Closed Closed Closed", "Mon Closed Tue Closed Wed Closed")

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
