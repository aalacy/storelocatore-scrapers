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
    locator_domain = "https://dominos.com.cn/"
    api_url = f"https://m8api.dominos.com.cn/dominos/menu/o-s-ms/misc.service/getStoreListByXY?longitude={str(long)}&latitude={str(lat)}&channelId=2&channelCode=WEB"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "clientId": "c17963f7ac1dd19d9c7c4aac7d071ef3",
        "signValue": "73eb594853b4a83145f1ae416ee74f7d",
        "dmClientVer": "EC-WAP-0-3.1.0.2022.04.18.PM-PC-0-FIREFOX-90.0",
        "dmSignature": "f4f340f16af58b3a58c45c81b6a0c247",
        "dmAppid": "dominosH5",
        "dmSequence": "1651040459632001",
        "Origin": "https://dominos.com.cn",
        "Connection": "keep-alive",
        "Referer": "https://dominos.com.cn/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }

    session = SgRequests()

    r = session.get(api_url, headers=headers)

    js = r.json()["data"]

    for j in js:

        page_url = "https://dominos.com.cn/selectAddress"
        location_name = j.get("storeName")
        ad = j.get("storeAddressEN")
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        city = j.get("cityNameEN") or "<MISSING>"
        state = j.get("districtNameCN") or "<MISSING>"
        postal = j.get("cityCode") or "<MISSING>"
        country_code = "CN"
        phone = j.get("storeTel") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        store_number = j.get("storeCode") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if street_address == "Opening Soon":
            street_address = "<MISSING>"
            hours_of_operation = "Coming Soon"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.CHINA],
        max_search_distance_miles=20,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
