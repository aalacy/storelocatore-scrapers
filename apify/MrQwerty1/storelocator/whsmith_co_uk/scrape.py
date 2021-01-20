import csv

from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sgzip.static import static_coordinate_list, SearchableCountries


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


def get_ids(coord):
    lat, lon = coord
    session = SgRequests()

    data = {
        "dwfrm_storelocator_city": "",
        "dwfrm_storelocator_postalCode": "",
        "dwfrm_storelocator_storeName": "",
        "dwfrm_storelocator_searchPhrase": "",
        "dwfrm_storelocator_longitude": lon,
        "dwfrm_storelocator_latitude": lat,
        "dwfrm_storelocator_county": "",
    }

    r = session.post(
        "https://www.whsmith.co.uk/on/demandware.store/Sites-whsmith-Site/en_GB/Stores-FindStores",
        data=data,
    )
    tree = html.fromstring(r.text)

    return tree.xpath("//li[@data-id]/@data-id")


def get_data(_id):
    locator_domain = "https://www.whsmith.co.uk/"
    page_url = f"https://www.whsmith.co.uk/stores/details?StoreID={_id.split('-')[1]}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1[@itemprop='name']/text()")).strip()
    street_address = (
        " ".join(
            ",".join(tree.xpath("//div[@itemprop='streetAddress']/text()")).split()
        )
        or "<MISSING>"
    )
    if street_address.endswith(","):
        street_address = street_address[:-1]

    city = (
        "".join(tree.xpath("//div[@itemprop='addressLocality']/text()")).strip()
        or "<MISSING>"
    )
    state = (
        "".join(tree.xpath("//div[@itemprop='addressRegion']/text()")).strip()
        or "<MISSING>"
    )
    postal = (
        "".join(tree.xpath("//div[@itemprop='postalCode']/text()")).strip()
        or "<MISSING>"
    )
    country_code = (
        "".join(tree.xpath("//div[@itemprop='addressCountry']/text()")).strip()
        or "<MISSING>"
    )
    if country_code == "United Kingdom":
        country_code = "GB"

    store_number = _id.split("-")[-1]
    phone = (
        "".join(tree.xpath("//span[@itemprop='telephone']/text()"))
        .strip()
        .replace("Unavailable - Customer Services:", "")
        or "<MISSING>"
    )
    latitude = (
        "".join(tree.xpath("//meta[@itemprop='latitude']/@content")) or "<MISSING>"
    )
    longitude = (
        "".join(tree.xpath("//meta[@itemprop='longitude']/@content")) or "<MISSING>"
    )
    location_type = "<MISSING>"

    _tmp = []
    hours = tree.xpath("//div[@class='store-hours']/div[@class='store-day-wrapper']")
    for h in hours:
        day = "".join(h.xpath("./span[@class='store-day']/text()")).strip()
        time = "".join(h.xpath("./span[@class='store-time']/text()")).strip()
        _tmp.append(f"{day} {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if hours_of_operation.count("Closed") >= 7:
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
    _ids = set()
    coords = static_coordinate_list(radius=20, country_code=SearchableCountries.BRITAIN)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_ids, coord): coord for coord in coords}
        for future in futures.as_completed(future_to_url):
            ids = future.result()
            for _id in ids:
                if _id.find("footer") == -1:
                    _ids.add(_id)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, _id): _id for _id in _ids}
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
