from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:

    tmp = []
    for h in hours:
        day = (
            str(h.get("day"))
            .replace("0", "Sunday")
            .replace("1", "Monday")
            .replace("2", "Tuesday")
            .replace("3", "Wednesday")
            .replace("4", "Thursday")
            .replace("5", "Friday")
            .replace("6", "Saturday")
        )
        opens = str(h.get("starthours"))
        opens = opens[:-2] + ":" + opens[-2:]
        closes = str(h.get("endhours"))
        closes = closes[:-2] + ":" + closes[-2:]
        line = f"{day} {opens} - {closes}"
        tmp.append(line)
    return "; ".join(tmp)


def get_drive_tru(drive_try) -> str:

    tmp = []
    for h in drive_try:
        day = (
            str(h.get("day"))
            .replace("0", "Sunday")
            .replace("1", "Monday")
            .replace("2", "Tuesday")
            .replace("3", "Wednesday")
            .replace("4", "Thursday")
            .replace("5", "Friday")
            .replace("6", "Saturday")
        )
        opens = str(h.get("starthours"))
        opens = opens[:-2] + ":" + opens[-2:]
        closes = str(h.get("endhours"))
        closes = closes[:-2] + ":" + closes[-2:]
        line = f"{day} {opens} - {closes}"
        tmp.append(line)
    return "; ".join(tmp)


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.ubt.com"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.ubt.com/locations",
        "content-type": "application/json",
        "Origin": "https://www.ubt.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    data = '{"operationName":null,"variables":{"tid":[812,842,814,820,786,791,840,817,818,813,811,831,824,830,837,823,828,826,833,839,834,827,832,848,776,835,838,825,836,829,895,"832"]},"query":"query ($tid: [String]) {\\n  terms: taxonomyTermQuery(limit: 1000, filter: {conditions: [{field: \\"tid\\", value: $tid}]}) {\\n    entities {\\n      title: entityLabel\\n      tid: entityId\\n      type: entityBundle\\n      created: entityCreated\\n      url: entityUrl {\\n        path\\n        __typename\\n      }\\n      ... on TaxonomyTermLocations {\\n        locationType: fieldLocationType {\\n          entity {\\n            title: entityLabel\\n            __typename\\n          }\\n          __typename\\n        }\\n        locationServices: fieldLocationServices {\\n          entity {\\n            title: entityLabel\\n            __typename\\n          }\\n          __typename\\n        }\\n        address: fieldAddress {\\n          addressLine1\\n          addressLine2\\n          state: administrativeArea\\n          city: locality\\n          zip: postalCode\\n          __typename\\n        }\\n        coordinates: fieldGeofield {\\n          lat\\n          lon\\n          __typename\\n        }\\n        phone: fieldPhoneNumber\\n        info: fieldLocationInfo\\n        lobbyHours: fieldLobbyHours {\\n          day\\n          starthours\\n          endhours\\n          __typename\\n        }\\n        driveThruHours: fieldDriveThruHours {\\n          day\\n          starthours\\n          endhours\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'
    r = session.post("https://www.ubt.com/graphql", headers=headers, data=data)
    js = r.json()

    for j in js["data"]["terms"]["entities"]:

        a = j.get("address")
        page_url = f"https://www.ubt.com{j.get('url').get('path')}"
        location_name = j.get("title") or "<MISSING>"
        location_type = "Branch"
        street_address = f"{a.get('addressLine1')} {a.get('addressLine2')}".strip()
        state = a.get("state")
        postal = a.get("zip")
        country_code = "US"
        city = a.get("city")
        latitude = j.get("coordinates").get("lat")
        longitude = j.get("coordinates").get("lon")
        phone = j.get("phone") or "<MISSING>"
        hours = j.get("lobbyHours") or "<MISSING>"
        drive_try = j.get("driveThruHours") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            hours_of_operation = get_hours(hours)
        if hours_of_operation == "<MISSING>":
            hours_of_operation = get_hours(drive_try) or "<MISSING>"

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
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
