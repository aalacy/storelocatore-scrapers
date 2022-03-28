from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    locator_domain = "https://www.tacobell.cl"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "content-type": "application/json",
        "X-ORION-DEVICEID": "ooG8bSvcI4MSXFj9Fp3ZNp28Sg8dLRUKuR6cSEl4nUH5D6FBfG",
        "X-ORION-FP": "f8d7d0d52f08feff7ae9980b5efcb38c",
        "X-ORION-DOMAIN": "www.tacobell.cl",
        "X-ORION-REFERRER": "",
        "X-ORION-TIMEZONE": "Europe/Zaporozhye",
        "X-ORION-PATHNAME": "/tiendas",
        "Origin": "https://www.tacobell.cl",
        "Connection": "keep-alive",
        "Referer": "https://www.tacobell.cl/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }

    params = (("operationName", "getWebsitePage_cached"),)

    data = '{"operationName":"getWebsitePage_cached","variables":{"pageId":"K4snRnDyobBZHmFvW","websiteId":"W9yGmwhA3boSbkE9j"},"query":"query getWebsitePage_cached($pageId: ID, $websiteId: ID) {\\n  page(pageId: $pageId, websiteId: $websiteId) {\\n    _id\\n    path\\n    activeComponents {\\n      _id\\n      options\\n      componentTypeId\\n      schedule {\\n        isScheduled\\n        latestScheduleStatus\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'

    r = session.post(
        "https://api.getjusto.com/graphql", headers=headers, params=params, data=data
    )
    js = r.json()["data"]["page"]["activeComponents"][0]["options"]["stores"]
    for j in js:
        try:
            otherText = "".join(j.get("otherText"))
        except:
            otherText = "<MISSING>"
        store_number = "<MISSING>"
        if otherText != "<MISSING>":
            store_number = otherText.split()[1].strip()
        page_url = "https://www.tacobell.cl/tiendas"
        location_name = j.get("name")
        place_id = j.get("placeId")
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
        country_code = "CL"
        city = ad.split(",")[-2].strip()
        latitude = js.get("data").get("place").get("location").get("lat")
        longitude = js.get("data").get("place").get("location").get("lng")

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=store_number,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.LATITUDE}))) as writer:
        fetch_data(writer)
