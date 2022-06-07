from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.nissan.co.uk/"
    api_url = "https://www.nissan.co.uk/content/nissan_prod/en_GB/index/dealer-finder/jcr:content/freeEditorial/contentzone_e70c/columns/columns12_5fe8/col1-par/find_a_dealer_14d.extended_dealers_by_location.json/_charset_/utf-8/page/1/size/600/data.json"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["dealers"]
    for j in js:
        a = j.get("address")
        slug = j.get("contact").get("website")
        page_url = f"https://www.nissan.co.uk{slug}"
        location_name = j.get("tradingName") or "<MISSING>"
        location_type = "<MISSING>"
        street_address = a.get("addressLine1") or "<MISSING>"
        state = "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = "GB"
        city = a.get("city") or "<MISSING>"
        store_number = j.get("urlId") or "<MISSING>"
        latitude = j.get("geolocation").get("latitude") or "<MISSING>"
        longitude = j.get("geolocation").get("longitude") or "<MISSING>"
        phone = j.get("contact").get("phone")
        hours_of_operation = (
            "".join(j.get("openingHours").get("openingHoursText"))
            .replace("<br>", " ")
            .replace("Sales:", "")
            .strip()
        )
        if hours_of_operation.find("Services & Parts:") != -1:
            hours_of_operation = hours_of_operation.split("Services & Parts:")[
                0
            ].strip()
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"

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
            raw_address=f"{street_address} {city}, {state} {postal}".replace(
                "<MISSING>", ""
            ).strip(),
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
