from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgpostal.sgpostal import International_Parser, parse_address
from lxml import html
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://honda.co.jp/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://shopsearch.honda.co.jp",
        "Connection": "keep-alive",
        "Referer": f"https://shopsearch.honda.co.jp/auto/search/?latitude={lat}&longitude={long}&searchWay=info",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }
    data = {
        "latitude": f"{lat}",
        "longitude": f"{long}",
        "requestType": "0",
        "searchMode": "local",
        "kyotenKbn": "",
        "qualitySelectFlg": "",
        "nsxFlg": "",
        "orangeDealerMasterFlg": "",
        "welfareParking": "",
        "welfareToilet": "",
        "welfareDealerFlg": "",
        "onlineReserveOpenFlg": "",
        "smallstoreShow": "",
        "extraFlg7": "",
        "extraFlg8": "",
        "od": "",
        "isNotZoom": "true",
        "isCondition": "false",
        "version": "3",
        "isCancelAccesslog": "true",
    }

    session = SgRequests()

    r = session.post(
        "https://shopsearch.honda.co.jp/front/dealer/ajax/doSearch.do",
        headers=headers,
        data=data,
    )

    js = r.json()["shopInfos"]
    for j in js:
        kanbanCd = j.get("kanbanCd")
        hojinCd = j.get("hojinCd")
        kyotenCd = j.get("kyotenCd")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://shopsearch.honda.co.jp",
            "Connection": "keep-alive",
            "Referer": f"https://shopsearch.honda.co.jp/auto/search/?latitude={latitude}&longitude={longitude}&searchWay=info",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "trailers",
        }

        data = {
            "rank": "1",
            "hojinCd": f"{hojinCd}",
            "kanbanCd": f"{kanbanCd}",
            "kyotenCd": f"{kyotenCd}",
            "requestType": "0",
            "centerLatitude": f"{latitude}",
            "centerLongitude": f"{longitude}",
        }
        r = session.post(
            "https://shopsearch.honda.co.jp/front/dealer/list/info.do",
            headers=headers,
            data=data,
        )

        tree = html.fromstring(r.text)

        page_url = f"https://shopsearch.honda.co.jp/auto/search/?latitude={latitude}&longitude={longitude}&searchWay=info"
        location_name = (
            "".join(tree.xpath('//div[contains(@class, "store-name")]//text()'))
            .replace("\n", "")
            .strip()
        )
        ad = (
            " ".join(tree.xpath('//div[contains(text(), "住所")]/text()'))
            .replace("\n", "")
            .replace("\r", "")
            .replace("■住所：", "")
            .strip()
        )
        ad = " ".join(ad.split())
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>":
            street_address = ad
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "JP"
        city = a.city or "<MISSING>"
        phone = (
            "".join(tree.xpath('//span[contains(text(), "電話番号")]/text()'))
            .replace("■電話番号：", "")
            .strip()
        )
        hours_of_operation_week = (
            "".join(tree.xpath('//span[contains(text(), "営業時間")]/text()'))
            .replace("\n", "")
            .replace("\r", "")
            .replace("■営業時間：", "")
            .strip()
        )
        hours_of_operation_weekend = (
            "".join(tree.xpath('//span[contains(text(), "休店日")]/text()'))
            .replace("\n", "")
            .replace("\r", "")
            .replace("■休店日：", "")
            .strip()
        )
        hours_of_operation = hours_of_operation_week + " " + hours_of_operation_weekend
        hours_of_operation = " ".join(hours_of_operation.split())

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
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.JAPAN],
        max_search_distance_miles=50,
        expected_search_radius_miles=50,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.1stbmt.com"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
