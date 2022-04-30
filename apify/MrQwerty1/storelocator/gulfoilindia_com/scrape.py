from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.gulfoilindia.com/wp-admin/admin-ajax.php?action=store_search&autoload=1"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        location_name = j.get("store") or ""
        location_name = (
            location_name.replace("&#8211;", "-")
            .replace("&#8217;", "'")
            .replace("&#038;", "&")
        )
        adr1 = j.get("address") or ""
        adr2 = j.get("address2") or ""
        street_address = f"{adr1} {adr2}".strip()
        if "E-mail" in street_address:
            street_address = street_address.split("E-mail")[0].strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country_code = "IN"
        store_number = j.get("id")
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = j.get("hours")

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
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.gulfoilindia.com/"
    page_url = "https://www.gulfoilindia.com/where-to-buy/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
