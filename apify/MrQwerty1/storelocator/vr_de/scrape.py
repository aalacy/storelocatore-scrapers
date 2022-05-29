from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    for i in range(1, 100):
        api = f"https://api.geno-datenhub.de/places?_per_page=1000&_page={i}&kind[]=bank&dynamic_attributes.teilnahme_vrde=true&_radius=20000&_fields[]=id&_fields[]=address&_fields[]=contact&_fields[]=kind&_fields[]=subtype&_fields[]=links&_fields[]=name&_fields[]=services&_fields[]=opening_hours&_fields[]=measure_code&_fields[]=is_open&_fields[]=institute&_fields[]=branch_name&_fields[]=uid_vrnet&_fields[]=alternative_bank_name&_fields[]=opening_hours_hint"
        r = session.get(api, headers=headers)
        js = r.json()["data"]
        if not js:
            break

        for j in js:
            a = j.get("address") or {}
            street_address = a.get("street")
            city = a.get("city")
            postal = a.get("zip_code")
            country_code = "DE"
            store_number = j.get("id")
            location_name = j.get("name")
            location_type = j["institute"]["bank_type"]
            try:
                page_url = j["links"]["detail_page_url"]
            except KeyError:
                page_url = SgRecord.MISSING
            phone = j["contact"]["i18n_phone_number"]
            latitude = a.get("latitude")
            longitude = a.get("longitude")

            _tmp = []
            hours = j.get("opening_hours") or {}
            for day, inters in hours.items():

                _t = []
                for i in inters:
                    _t.append(f'{"-".join(i)}')

                _tmp.append(f'{day}: {"|".join(_t)}')

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                store_number=store_number,
                location_type=location_type,
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.vr.de/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "token": "2MEN71Lg25DxWLysCqC94b2H",
        "Origin": "https://standorte.vr.de",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "cross-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Referer": "https://standorte.vr.de/",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
