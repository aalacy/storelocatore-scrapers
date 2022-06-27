from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return city, state, postal


def get_additional(_id):
    params = {
        "operationName": "getPlaceDetails_cached",
    }

    json_data = {
        "operationName": "getPlaceDetails_cached",
        "variables": {
            "placeId": _id,
        },
        "query": "query getPlaceDetails_cached($placeId: ID) {\n  place(placeId: $placeId) {\n    _id\n    text\n    secondaryText\n    location\n    __typename\n  }\n}\n",
    }

    r = session.post(api, headers=headers, params=params, json=json_data)
    j = r.json()["data"]["place"]
    street = j.get("text")
    csz = j.get("secondaryText")

    g = j.get("location") or {}
    lat = g.get("lat")
    lng = g.get("lng")

    return {"street": street, "csz": csz, "geo": (lat, lng)}


def fetch_data(sgw: SgWriter):
    params = {
        "operationName": "getWebsitePage_cached",
    }

    json_data = {
        "operationName": "getWebsitePage_cached",
        "variables": {
            "pageId": "fFxjG4spkojufQabf",
            "websiteId": "YABts5tqy8QqEFZfj",
        },
        "query": "query getWebsitePage_cached($pageId: ID, $websiteId: ID) {\n  page(pageId: $pageId, websiteId: $websiteId) {\n    _id\n    path\n    activeComponents {\n      _id\n      options\n      componentTypeId\n      schedule {\n        isScheduled\n        latestScheduleStatus\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
    }
    r = session.post(api, headers=headers, params=params, json=json_data)
    comp = r.json()["data"]["page"]["activeComponents"]

    for c in comp:
        js = c["options"]["stores"]
        for j in js:
            location_name = j.get("name")
            phone = j.get("phone")
            store_number = j.get("placeId")

            a = get_additional(store_number)
            street_address = a.get("street")
            csz = a.get("csz")
            city, state, postal = get_international(csz)
            latitude, longitude = a.get("geo") or (SgRecord.MISSING, SgRecord.MISSING)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="MX",
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                store_number=store_number,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.benedettis.com/"
    page_url = "https://www.benedettis.com/locales"
    api = "https://api.getjusto.com/graphql"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
