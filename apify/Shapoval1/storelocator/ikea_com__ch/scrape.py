from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.ikea.com/ch/en/"
    api_url = "https://www.ikea.com/ch/en/meta-data/navigation/stores-detailed.json?cb=adyik19i0n"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = j.get("storePageUrl") or "<MISSING>"
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("address").get("street") or "<MISSING>"
        state = j.get("address").get("stateProvinceCode") or "<MISSING>"
        postal = j.get("address").get("zipCode") or "<MISSING>"
        country_code = "CH"
        city = j.get("address").get("city") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        hours = j.get("hours").get("normal")
        tmp = []
        hours_of_operation = "<MISSING>"
        if hours:
            for h in hours:
                day = h.get("day")
                opens = h.get("open")
                closes = h.get("close")
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)

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
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)

    locator_domain = "https://www.ikea.com/at/de/"
    api_url = "https://www.ikea.com/at/de/meta-data/navigation/stores-detailed.json?cb=66puuyybpg"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = j.get("storePageUrl") or "<MISSING>"
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("address").get("street") or "<MISSING>"
        state = j.get("address").get("stateProvinceCode") or "<MISSING>"
        postal = j.get("address").get("zipCode") or "<MISSING>"
        country_code = "AT"
        city = j.get("address").get("city") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        hours = j.get("hours").get("normal")
        tmp = []
        hours_of_operation = "<MISSING>"
        if hours:
            for h in hours:
                day = h.get("day")
                opens = h.get("open")
                closes = h.get("close")
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)

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
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
