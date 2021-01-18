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
        "dwfrm_storelocator_countryCode": "GB",
        "dwfrm_storelocator_latitude": lat,
        "dwfrm_storelocator_longitude": lon,
        "dwfrm_storelocator_departments": "",
        "wideSearch": "false",
        "dwfrm_storelocator_findbylocation": "",
    }

    r = session.post(
        "https://www.gap.co.uk/on/demandware.store/Sites-ShopUK-Site/en_GB/Stores-Find",
        data=data,
    )
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//div[@class='js-store-result js-store-result-box store-search-page__result']/@data-id"
    )


def get_data(_id):
    locator_domain = "https://www.gap.co.uk/"
    page_url = f"https://www.gap.co.uk/storesinformation?StoreID={_id}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1[@itemprop='name']/text()")).strip()
    street_address = (
        "".join(tree.xpath("//span[@itemprop='streetAddress']/text()")).strip()
        or "<MISSING>"
    )
    city = (
        "".join(tree.xpath("//span[@itemprop='addressLocality']/text()")).strip()
        or "<MISSING>"
    )
    state = "<MISSING>"
    postal = (
        "".join(tree.xpath("//span[@itemprop='postalCode']/text()")).strip()
        or "<MISSING>"
    )
    country_code = (
        "".join(tree.xpath("//span[@itemprop='addressCountry']/text()")).strip()
        or "<MISSING>"
    )
    if country_code == "United Kingdom":
        country_code = "GB"
    else:
        return
    store_number = _id
    phone = (
        "".join(tree.xpath("//span[@itemprop='telephone']/text()")).strip()
        or "<MISSING>"
    )
    latitude = "".join(tree.xpath("//div[@data-lat]/@data-lat")) or "<MISSING>"
    longitude = "".join(tree.xpath("//div[@data-lat]/@data-lng")) or "<MISSING>"
    location_type = (
        "".join(tree.xpath("//div[@class='store-locator-details__details']/text()"))
        .strip()[:-1]
        .strip()
        or "<MISSING>"
    )
    if location_type.startswith(","):
        location_type = location_type.replace(",", "").strip()

    try:
        hours_of_operation = (
            "".join(tree.xpath("//span[@class='store-hours']/p")[-1].xpath("./text()"))
            .replace("\n", ";")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation.lower().find("closed") != -1:
            hours_of_operation = "Closed"
    except IndexError:
        hours_of_operation = "<MISSING>"

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
