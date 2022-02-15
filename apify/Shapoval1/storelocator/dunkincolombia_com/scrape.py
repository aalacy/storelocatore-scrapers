from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        days = h.get("days")
        time = h.get("schedule")
        line = f"{days} {time}"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp)
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.dunkincolombia.com"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-ORION-DEVICEID": "rShA4ktuLVLnIKu3fE9zQa2CxwHBALOtAVwutQWAYJRHfk11Up",
        "X-ORION-FP": "f8d7d0d52f08feff7ae9980b5efcb38c",
        "X-ORION-DOMAIN": "www.dunkincolombia.com",
        "X-ORION-REFERRER": "",
        "X-ORION-TIMEZONE": "Europe/Zaporozhye",
        "X-ORION-PATHNAME": "/restaurantes",
        "Origin": "https://www.dunkincolombia.com",
        "Connection": "keep-alive",
        "Referer": "https://www.dunkincolombia.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }

    params = (("operationName", "getStoresZones"),)

    json_data = {
        "operationName": "getStoresZones",
        "variables": {
            "websiteId": "cRyFRFomeept9LCwn",
        },
        "query": "query getStoresZones($websiteId: ID) {\n  stores(websiteId: $websiteId) {\n    items {\n      _id\n      name\n      phone\n      humanSchedule {\n        days\n        schedule\n        __typename\n      }\n      acceptDelivery\n      acceptGo\n      zones {\n        _id\n        deliveryLimits\n        __typename\n      }\n      address {\n        placeId\n        location\n        address\n        addressSecondary\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
    }

    r = session.post(
        "https://api.getjusto.com/graphql",
        headers=headers,
        params=params,
        json=json_data,
    )
    js = r.json()["data"]["stores"]["items"]
    for j in js:

        a = j.get("address")
        page_url = "https://www.dunkincolombia.com/restaurantes"
        location_name = j.get("name") or "<MISSING>"
        street_address = a.get("address") or "<MISSING>"
        if street_address == "undefined":
            street_address = "<MISSING>"
        ad = "".join(a.get("addressSecondary"))
        country_code = "CO"
        city = ad.split(",")[0].strip() or "<MISSING>"
        if ad.find("Bogotá") != -1:
            city = "Bogotá"
        latitude = a.get("location").get("lat") or "<MISSING>"
        longitude = a.get("location").get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        hours = j.get("humanSchedule") or "<MISSING>"
        if hours != "<MISSING>":
            hours_of_operation = get_hours(hours)

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
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
