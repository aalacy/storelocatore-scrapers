import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_js():
    data = {
        "request": {
            "appkey": "4E0CC702-70E5-11E8-923C-16F58D89CD5A",
            "formdata": {
                "dataview": "store_default",
                "limit": 5000,
                "geolocs": {
                    "geoloc": [
                        {
                            "addressline": "30313",
                            "country": "",
                            "latitude": "",
                            "longitude": "",
                        }
                    ]
                },
                "searchradius": "5000",
                "where": {"country": {"eq": "US"}},
            },
        }
    }

    r = session.post(
        "https://hosted.where2getit.com/ddsdiscounts/rest/locatorsearch",
        data=json.dumps(data),
    )
    js = r.json()["response"]["collection"]
    return js


def fetch_data(sgw: SgWriter):
    js = get_js()
    for j in js:
        location_name = j.get("name1")
        street_address = f"{j.get('address1')} {j.get('address2') or ''}".strip()
        city = j.get("city")
        postal = j.get("postalcode")
        country_code = j.get("country")
        state = j.get("state")
        store_number = j.get("clientkey")
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

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
            _tmp.append(f'{day.capitalize()} {j.get(f"{day}")}')

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
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
    locator_domain = "https://ddsdiscounts.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
