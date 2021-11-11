import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    page_url = "https://www.wolfordshop.co.uk/stores"

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var storesJson =')]/text()"))
    text = text.split("var storesJson =")[1].strip()[:-1]
    js = json.loads(text)

    for j in js:
        street_address = j.get("address1")
        country_code = j.get("countryCode")

        if country_code == "US":
            city = j.get("city")
            if "," not in city:
                line = j.get("postalCode")
                state = line.split()[0]
                postal = line.split()[-1]
            else:
                postal = j.get("postalCode")
                state = city.split(",")[-1].strip()
                city = city.split(",")[0].strip()
            if postal == state:
                state = SgRecord.MISSING
        elif country_code == "CA":
            postal = j.get("postalCode").replace("QC ", "")
            line = j.get("city")
            city = line.split(",")[0].strip()
            state = line.split(",")[-1].strip()
        elif country_code == "GB":
            city = j.get("city")
            state = SgRecord.MISSING
            postal = j.get("postalCode")
        else:
            city = j.get("city")
            state = SgRecord.MISSING
            postal = j.get("postalCode")

        if postal == ".":
            postal = SgRecord.MISSING

        store_number = j.get("storeID")
        location_name = j.get("name")
        phone = j.get("phone") or ""
        if ";" in phone:
            phone = phone.split(";")[0].strip()
        if "," in phone:
            phone = phone.split(",")[0].strip()

        latitude = j.get("latitude")
        longitude = j.get("longitude")

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
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.wolfordshop.co.uk/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
