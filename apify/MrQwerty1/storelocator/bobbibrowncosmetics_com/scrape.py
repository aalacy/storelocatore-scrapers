from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def clean_phone(text):
    text = text.lower()
    replace_list = ["(", ")", ".", "tel", ":", "+"]
    black_list = ["e", "x", "d"]
    for r in replace_list:
        text = text.replace(r, "").strip()
    for b in black_list:
        if b in text:
            text = text.split(b)[0].strip()

    return text


def fetch_data(sgw: SgWriter):
    api = "https://www.bobbibrowncosmetics.com/rpc/jsonrpc.tmpl"
    r = session.post(api, params=params, data=data)
    js = r.json()[0]["result"]["value"]["results"].values()

    for j in js:
        location_name = j.get("DOORNAME")
        street_address = " ".join(
            f'{j.get("ADDRESS")} {j.get("ADDRESS2") or ""}'.split()
        )
        city = j.get("CITY") or ""
        state = j.get("STATE_OR_PROVINCE") or ""
        postal = j.get("ZIP_OR_POSTAL") or ""
        postal = postal.replace("-", "")
        country = j.get("COUNTRY")
        raw_address = " ".join(f"{street_address} {city} {state} {postal}".split())

        phone = j.get("PHONE1") or ""
        phone = clean_phone(phone)
        latitude = j.get("LATITUDE")
        longitude = j.get("LONGITUDE")
        location_type = j.get("STORE_TYPE")
        store_number = j.get("DOOR_ID")
        hours_of_operation = j.get("STORE_HOURS")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            location_type=location_type,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.bobbibrowncosmetics.com/"
    page_url = "https://www.bobbibrowncosmetics.com/store_locator"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "*/*",
    }

    params = (("dbgmethod", "locator.doorsandevents"),)

    data = {
        "JSONRPC": '[{"method":"locator.doorsandevents","id":3,"params":[{"fields":"DOOR_ID, DOORNAME, EVENT_NAME, EVENT_START_DATE, EVENT_END_DATE, EVENT_IMAGE, EVENT_FEATURES, EVENT_TIMES, SERVICES, STORE_HOURS, ADDRESS, ADDRESS2, STATE_OR_PROVINCE, CITY, REGION, COUNTRY, ZIP_OR_POSTAL, PHONE1, STORE_TYPE, LONGITUDE, LATITUDE","radius":"6000","country":"United Kingdom","region_id":"0,47,27","latitude":51.5072178,"longitude":-0.1275862,"uom":"mile","_TOKEN":"97c4d4b5d9b8803ccf9440fe781206a3aabff824,26fb46c93f3cc9fb25d01b63333e968ee603ceda,1642674820"}]}]'
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
