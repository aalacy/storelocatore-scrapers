from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://crab-station.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://crabstation.revelup.online/",
        "x-oo-xt-loaded-modules": '["branding","frontend"]',
        "Origin": "https://crabstation.revelup.online",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }

    json_data = {
        "operationName": "storeList",
        "variables": {},
        "query": "query storeList {\n  establishments {\n    id\n    name\n    businessName\n    description\n    address {\n      line1\n      line2\n      city\n      state\n      country\n      zipCode\n      latitude\n      longitude\n      __typename\n    }\n    timetable {\n      currentDay\n      timetables {\n        offsetFromCurrentDay\n        workingHours {\n          start\n          end\n          __typename\n        }\n        note\n        __typename\n      }\n      __typename\n    }\n    settings {\n      diningOptions {\n        value\n        label\n        __typename\n      }\n      isCateringEnabled\n      timezone\n      timeFormat\n      isEnabledMarketingOptInOut\n      __typename\n    }\n    __typename\n  }\n}\n",
    }

    r = session.post(
        "https://crabstation.mw.revelup.online/graphql", headers=headers, json=json_data
    )
    js = r.json()["data"]["establishments"]
    for j in js:

        location_name = j.get("name") or "<MISSING>"
        location_type = j.get("description") or "<MISSING>"
        a = j.get("address")
        street_address = f"{a.get('line1')} {a.get('line2')}".strip() or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zipCode") or "<MISSING>"
        country_code = "US"
        city = a.get("city") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        page_url = f"https://crabstation.revelup.online/store/{store_number}"
        latitude = a.get("latitude") or "<MISSING>"
        longitude = a.get("longitude") or "<MISSING>"
        json_data = {
            "operationName": "storeInfo",
            "variables": {
                "storeId": int(store_number),
            },
            "query": "query storeInfo($storeId: Int!) {\n  establishments(establishmentId: $storeId) {\n    address {\n      line1\n      line2\n      city\n      state\n      country\n      zipCode\n      latitude\n      longitude\n      __typename\n    }\n    phoneNumber\n    __typename\n  }\n  timetables(establishmentIds: [$storeId]) {\n    currentDay\n    storeAvailability {\n      isStoreOpen\n      isOnlineOrderingAvailable\n      nextOpenTime {\n        startHours\n        offsetFromCurrentDay\n        __typename\n      }\n      __typename\n    }\n    timetables {\n      offsetFromCurrentDay\n      workingHours {\n        start\n        end\n        __typename\n      }\n      note\n      __typename\n    }\n    __typename\n  }\n}\n",
        }

        r = session.post(
            "https://crabstation.mw.revelup.online/graphql",
            headers=headers,
            json=json_data,
        )
        js = r.json()["data"]
        phone = js.get("establishments")[0].get("phoneNumber")
        hours_of_operation = "<INACCESSIBLE>"

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
