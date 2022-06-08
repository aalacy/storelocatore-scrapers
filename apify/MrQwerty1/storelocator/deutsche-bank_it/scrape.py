from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch
from tenacity import retry, stop_after_attempt, wait_fixed


@retry(stop=stop_after_attempt(10), wait=wait_fixed(5))
def get_js(api):
    r = session.get(api, headers=headers)
    js = r.json()["data"]

    return js


def fetch_data(sgw: SgWriter):
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.ITALY], expected_search_radius_miles=50
    )
    for lat, lng in search:
        api = f"https://secure.deutschebank.it/pac/api/v1/sl/nearestbranches?multiple_search=&lat={lat}&lng={lng}&tipologia=sportello_ufficio"
        js = get_js(api)

        for j in js:
            street_address = j.get("address")
            city = j.get("comune")
            state = j.get("provincia")
            postal = j.get("cap")
            country_code = "IT"
            store_number = j.get("id")
            location_name = j.get("business_line")
            phone = j.get("tel_filiale") or ""
            if "-" in phone:
                phone = phone.split("-")[0].strip()
            latitude = j.get("lat")
            longitude = j.get("lng")
            search.found_location_at(latitude, longitude)

            _tmp = []
            inters = []

            morning = f'{j.get("apertura_am")}-{j.get("chiusura_am")}'
            if "None" not in morning and "False" not in morning:
                inters.append(morning)

            evening = f'{j.get("apertura_pm")}-{j.get("chiusura_pm")}'
            if "None" not in evening and "False" not in evening:
                inters.append(evening)

            if inters:
                _tmp.append(f'Mon-Fri: {"|".join(inters)}')

            inters = []

            sat_morning = (
                f'{j.get("saturday_apertura_am")}-{j.get("saturday_chiusura_am")}'
            )
            if "None" not in sat_morning and "False" not in sat_morning:
                inters.append(sat_morning)

            sat_evening = (
                f'{j.get("saturday_apertura_pm")}-{j.get("saturday_chiusura_pm")}'
            )
            if "None" not in sat_evening and "False" not in sat_evening:
                inters.append(sat_evening)

            if inters:
                _tmp.append(f'Sat: {"|".join(inters)}')

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
    locator_domain = "https://deutsche-bank.it/"
    page_url = "https://entraincontatto.deutsche-bank.it/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
