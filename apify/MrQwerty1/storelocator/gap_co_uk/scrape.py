from concurrent import futures
from lxml import html

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests
from sgzip.static import static_coordinate_list, SearchableCountries


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

    if "," in location_type:
        location_name = "Gap"
    else:
        location_name = location_type

    hours = tree.xpath("//span[@class='store-hours']//text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = (
        ";".join(hours)
        .replace(
            "due to covid restrictions this store is temporarily closed, please visit www.gap.co.uk;",
            "",
        )
        .replace("p>;", "")
        .replace(";>", "")
        or "<MISSING>"
    )

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


def fetch_data(sgw: SgWriter):
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
            out = future.result()
            if out:
                sgw.write_row(
                    SgRecord(
                        locator_domain=out[0],
                        page_url=out[1],
                        location_name=out[2],
                        street_address=out[3],
                        city=out[4],
                        state=out[5],
                        zip_postal=out[6],
                        country_code=out[7],
                        store_number=out[8],
                        phone=out[9],
                        location_type=out[10],
                        latitude=out[11],
                        longitude=out[12],
                        hours_of_operation=out[13],
                    )
                )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
