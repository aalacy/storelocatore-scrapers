import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_json():
    r = session.get("https://www.rei.com/map/store")
    tree = html.fromstring(r.text)
    j = "".join(tree.xpath("//script[@id='modelData']/text()"))
    js_list = json.loads(j)
    return js_list["pageData"]["allStores"]["storeLocatorDataQueryModelList"]


def fetch_data(sgw: SgWriter):
    js_list = get_json()

    for d in js_list:
        j = d.get("storeDataModel")
        page_url = f"https://www.rei.com/{j['storePageUrl']}"
        location_name = j.get("storeName")
        street_address = j.get("address1")
        city = j.get("city")
        state = j.get("stateCode")
        postal = j.get("zip")
        country_code = j.get("countryCode")
        store_number = j.get("storeNumber")
        phone = j.get("phoneNumber")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = j.get("Type")

        hours = j.get("storeHours")
        _tmp = []
        for h in hours:
            day = h.get("days")
            start = h.get("openAt")
            end = h.get("closeAt")
            _tmp.append(f"{day}  {start} - {end}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        if j.get("storeOpeningSoon"):
            hours_of_operation = "Coming Soon"

        row = SgRecord(
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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.rei.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
