from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://burgerking.cl/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://delivery.burgerking.cl/",
        "X-ORION-DEVICEID": "MI9auMmu6xgCrE4mgx4mY4I3Zv9jQ1Y3E33nImlfERK6rR7mgz",
        "X-ORION-FP": "68f5767032e606c379b950c6ff6abb86",
        "X-ORION-DOMAIN": "delivery.burgerking.cl",
        "X-ORION-TIMEZONE": "Europe/Zaporozhye",
        "X-ORION-PATHNAME": "/locales",
        "Origin": "https://delivery.burgerking.cl",
        "Proxy-Authorization": "Basic ZG1pdHJpeTIyc2hhcGFAZ21haWwuY29tOnJxeFN6YzI0NnNzdnByVVZwdHJT",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
    }

    params = {
        "operationName": "getStoresZones",
    }

    json_data = {
        "operationName": "getStoresZones",
        "variables": {
            "websiteId": "pPFvY6qcd7boWbpys",
        },
        "query": "query getStoresZones($websiteId: ID) {\n  stores(websiteId: $websiteId) {\n    items {\n      _id\n      name\n      phone\n      supportOptions {\n        phone\n        __typename\n      }\n      humanSchedule {\n        days\n        schedule\n        __typename\n      }\n      acceptDelivery\n      acceptGo\n      zones {\n        _id\n        deliveryLimits\n        __typename\n      }\n      address {\n        placeId\n        location\n        address\n        addressSecondary\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
    }

    r = session.post(
        "https://websites-api.getjusto.com/graphql",
        params=params,
        headers=headers,
        json=json_data,
    )
    js = r.json()["data"]["stores"]["items"]
    for j in js:

        a = j.get("address")
        page_url = "https://delivery.burgerking.cl/locales"
        location_name = j.get("name") or "<MISSING>"
        ad = "".join(a.get("addressSecondary"))
        street_address = a.get("address") or "<MISSING>"
        country_code = "CL"
        city = ad.split(",")[0].strip()
        latitude = a.get("location").get("lat")
        longitude = a.get("location").get("lng")
        phone = j.get("phone") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        hours = j.get("humanSchedule")
        tmp = []
        if hours:
            for h in hours:
                day = h.get("days")
                times = h.get("schedule")
                line = f"{day} {times}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
