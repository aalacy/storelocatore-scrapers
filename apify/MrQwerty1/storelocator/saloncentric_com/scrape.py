import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data(sgw):
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=500
    )
    for _zip in search:
        data = {
            "request": {
                "appkey": "C8F922C2-35CF-11E3-8171-DA43842CA48B",
                "formdata": {
                    "dataview": "store_default",
                    "limit": 1000,
                    "geolocs": {
                        "geoloc": [
                            {
                                "addressline": _zip,
                                "country": "",
                                "latitude": "",
                                "longitude": "",
                            }
                        ]
                    },
                    "searchradius": "1000",
                },
            }
        }

        r = session.post(
            "https://hosted.where2getit.com/saloncentric/rest/locatorsearch",
            data=json.dumps(data),
        )

        try:
            js = r.json()["response"]["collection"]
        except:
            js = []

        for j in js:
            location_name = (
                f"SalonCentric - {j.get('name')} Professional Beauty Supply Store"
            )
            street_address = j.get("address1")
            city = j.get("city")
            state = j.get("state")
            postal = j.get("postalcode")
            country_code = j.get("country")
            store_number = j.get("clientkey")
            if len(store_number) > 4:
                continue

            phone = j.get("phone")
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            page_url = f"https://stores.saloncentric.com/{state.lower()}/{city.replace(' ', '-').lower()}/{store_number}/"

            days = [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]
            _tmp = []
            for day in days:
                start = j.get(f"{day}_hours_open") or ""
                close = j.get(f"{day}_hours_closed") or ""
                if not start or not close:
                    continue
                if "CLOSED" not in start and "CLOSED" not in close:
                    _tmp.append(f"{day[:3].upper()}: {start} - {close}")
                else:
                    _tmp.append(f"{day[:3].upper()}: CLOSED")

            hours_of_operation = ";".join(_tmp)

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
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.saloncentric.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
