from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.tacobell.com.pe"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "content-type": "application/json",
        "X-ORION-DEVICEID": "QdKhvxynuH7icwdfTgqlBnPc3AV0ewEbQSPG7i4q3VHqmsbGYZ",
        "X-ORION-FP": "f8d7d0d52f08feff7ae9980b5efcb38c",
        "X-ORION-DOMAIN": "www.tacobell.com.pe",
        "X-ORION-REFERRER": "",
        "X-ORION-TIMEZONE": "Europe/Zaporozhye",
        "X-ORION-PATHNAME": "/locales",
        "Origin": "https://www.tacobell.com.pe",
        "Connection": "keep-alive",
        "Referer": "https://www.tacobell.com.pe/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "TE": "trailers",
    }

    params = (("operationName", "getWebsitePage_cached"),)

    data = '{"operationName":"getWebsitePage_cached","variables":{"pageId":"K7G7wFx8qfrdg77ab","websiteId":"QHTZYR9uvEpC4MZdu"},"query":"query getWebsitePage_cached($pageId: ID, $websiteId: ID) {\\n  page(pageId: $pageId, websiteId: $websiteId) {\\n    _id\\n    path\\n    activeComponents {\\n      _id\\n      options\\n      componentTypeId\\n      schedule {\\n        isScheduled\\n        latestScheduleStatus\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'

    r = session.post(
        "https://api.getjusto.com/graphql", headers=headers, params=params, data=data
    )
    js = r.json()["data"]["page"]["activeComponents"][0]["options"]["stores"]
    for j in js:

        hours_of_operation = "".join(j.get("otherText")).split("Horarios:")[1].strip()
        place_id = j.get("placeId")
        location_name = j.get("name")

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "content-type": "application/json",
            "X-ORION-DEVICEID": "vcagLCBH7sBjOZNVZFPi9K18TinEZv1aVRvjgn4eQzUlaWYJUX",
            "X-ORION-FP": "f8d7d0d52f08feff7ae9980b5efcb38c",
            "X-ORION-DOMAIN": "www.tacobell.com.pe",
            "X-ORION-REFERRER": "",
            "X-ORION-TIMEZONE": "Europe/Zaporozhye",
            "X-ORION-PATHNAME": "/locales",
            "Origin": "https://www.tacobell.com.pe",
            "Connection": "keep-alive",
            "Referer": "https://www.tacobell.com.pe/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "Cache-Control": "max-age=0",
            "TE": "trailers",
        }

        params = (("operationName", "getPlaceDetails_cached"),)

        data = (
            '{"operationName":"getPlaceDetails_cached","variables":{"placeId":"'
            + place_id
            + '"},"query":"query getPlaceDetails_cached($placeId: ID) {\\n  place(placeId: $placeId) {\\n    _id\\n    text\\n    secondaryText\\n    location\\n    __typename\\n  }\\n}\\n"}'
        )

        r = session.post(
            "https://api.getjusto.com/graphql",
            headers=headers,
            params=params,
            data=data,
        )
        js = r.json()
        street_address = js.get("data").get("place").get("text")
        ad = "".join(js.get("data").get("place").get("secondaryText"))
        country_code = "Perú"
        city = ad.split(",")[-2].strip()
        latitude = js.get("data").get("place").get("location").get("lat")
        longitude = js.get("data").get("place").get("location").get("lng")
        page_url = "https://www.tacobell.com.pe/locales"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
