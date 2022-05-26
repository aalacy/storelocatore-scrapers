import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//div[contains(text(), 'dataList')]/text()"))
    text = text.split('"dataList":')[1].split("CustomStoreLocator")[0].strip()[:-1]
    js = json.loads(text)

    for s in js:
        jj = s.get("PhysicalStore") or []
        for j in jj:
            adr = j.get("addressLine") or []
            street_address = ", ".join(adr)
            city = j.get("city")
            state = j.get("stateOrProvinceName")
            postal = j.get("postalCode") or ""
            postal = postal.strip()
            country_code = "MX"
            store_number = j.get("uniqueID")
            location_name = j["Description"][0]["displayStoreName"]
            phone = j.get("telephone1")
            latitude = j.get("latitude")
            longitude = j.get("longitude")

            try:
                hours_of_operation = j["Attribute"][0]["displayValue"] or ""
                if "inactiv" in hours_of_operation:
                    hours_of_operation = "Temporarily Closed"
            except:
                hours_of_operation = SgRecord.MISSING

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                store_number=store_number,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.dportenis.mx/"
    page_url = "https://www.dportenis.mx/AjaxStoreLocatorDisplayView?catalogId=3074457345616677668&storeId=1&langId=-5"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
