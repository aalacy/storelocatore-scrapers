import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw):
    postals = ["98837", "68822", "10001"]
    for p in postals:
        data = {
            "request": {
                "appkey": "C8F922C2-35CF-11E3-8171-DA43842CA48B",
                "formdata": {
                    "dataview": "store_default",
                    "limit": 1000,
                    "geolocs": {
                        "geoloc": [
                            {
                                "addressline": p,
                                "country": "",
                                "latitude": "",
                                "longitude": "",
                            }
                        ]
                    },
                    "searchradius": "5000",
                },
            }
        }

        r = session.post(
            "https://hosted.where2getit.com/saloncentric/rest/locatorsearch",
            data=json.dumps(data),
        )

        js = r.json()["response"]["collection"]

        for j in js:
            location_name = (
                f"SalonCentric - {j.get('name')} Professional Beauty Supply Store"
            )
            street_address = j.get("address1") or "<MISSING>"
            city = j.get("city") or "<MISSING>"
            state = j.get("state") or "<MISSING>"
            postal = j.get("postalcode") or "<MISSING>"
            country_code = j.get("country") or "<MISSING>"
            store_number = j.get("clientkey")
            if len(store_number) > 4:
                continue

            phone = j.get("phone") or "<MISSING>"
            latitude = j.get("latitude") or "<MISSING>"
            longitude = j.get("longitude") or "<MISSING>"
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
                start = j.get(f"{day}_hours_open")
                close = j.get(f"{day}_hours_closed")
                if not start or not close:
                    continue
                if start.find("CLOSED") == -1 and close.find("CLOSED") == -1:
                    _tmp.append(f"{day[:3].upper()}: {start} - {close}")
                else:
                    _tmp.append(f"{day[:3].upper()}: CLOSED")

            hours_of_operation = ";".join(_tmp) or SgRecord.MISSING

            if hours_of_operation.count("CLOSED") == 7:
                hours_of_operation = "CLOSED"

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
