from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://tiendas.movistar.es/pages_api/v1/locations"
    r = session.get(api, headers=headers)
    js = r.json()["locations"]

    for j in js:
        street_address = j.get("street_address")
        city = j.get("locality")
        state = j.get("region")
        postal = j.get("postcode")
        country_code = "ES"
        store_number = j.get("external_id")
        location_name = j.get("name")
        try:
            page_url = j["pages"]["store-page"]
        except KeyError:
            page_url = SgRecord.MISSING
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")

        _tmp = []
        hours = j.get("hours") or {}
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        for day in days:
            ints = hours.get(day)
            if not ints:
                _tmp.append(f"{day.title()}: Closed")
            else:
                inters = []
                for i in ints:
                    start = i.get("from")
                    end = i.get("to")
                    inters.append(f"{start}-{end}")
                inter = "|".join(inters)
                _tmp.append(f"{day.title()}: {inter}")

        hours_of_operation = ";".join(_tmp)

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
    locator_domain = "https://movistar.es/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
