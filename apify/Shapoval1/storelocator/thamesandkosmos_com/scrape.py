from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgpostal.sgpostal import International_Parser, parse_address
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://www.thamesandkosmos.com/"
    api_url = f"https://www.thamesandkosmos.com/index.php?option=com_storelocator&view=map&format=raw&searchall=0&Itemid=145&lat={str(lat)}&lng={str(long)}&radius=10000&catid=-1&tagid=2&featstate=0&name_search="

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }

    session = SgRequests()

    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath("//markers/marker")
    for d in div:

        page_url = "https://www.thamesandkosmos.com/index.php/about-us/store-locator"
        location_name = "".join(d.xpath(".//name/text()"))
        ad = "".join(d.xpath(".//address/text()"))
        location_type = "Brick-and-Mortar Store"
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "CA"
        if postal.isdigit():
            country_code = "US"
        city = a.city or "<MISSING>"
        if ad.find("1593 Barrington St.,") != -1:
            street_address = ad.split(",")[0].strip()
            city = ad.split(",")[1].strip()
            state = ad.split(",")[2].strip()
            postal = ad.split(",")[3].strip()
            country_code = "CA"

        latitude = "".join(d.xpath(".//lat/text()")) or "<MISSING>"
        longitude = "".join(d.xpath(".//lng/text()")) or "<MISSING>"
        phone = "".join(d.xpath(".//phone/text()")) or "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=100,
        expected_search_radius_miles=100,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
