import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_js(param):
    data = {
        "request": {
            "appkey": "6E3ECEB6-B58F-11E6-9AC3-9C37D1784D66",
            "formdata": {
                "dataview": "store_default",
                "limit": 5000,
                "geolocs": {
                    "geoloc": [
                        {
                            "addressline": param["addressline"],
                            "country": "",
                            "latitude": "",
                            "longitude": "",
                        }
                    ]
                },
                "searchradius": "3000",
                "where": {"country": {"eq": param["country"]}},
            },
        }
    }

    r = session.post(
        "https://hosted.where2getit.com/michaels/rest/locatorsearch",
        data=json.dumps(data),
    )
    js = r.json()["response"]["collection"]
    return js


def fetch_data(sgw: SgWriter):
    params = [
        {"addressline": "T9H 4G9", "country": "CA"},
        {"addressline": "99507", "country": "US"},
        {"addressline": "30313", "country": "US"},
        {"addressline": "84602", "country": "US"},
    ]

    for p in params:
        js = get_js(p)

        for j in js:
            location_type = SgRecord.MISSING
            if j.get("comingsoon"):
                location_type = "Coming Soon"
            location_name = f"Michaels, {j.get('name')}"
            street_address = j.get("address1")
            city = j.get("city")
            postal = j.get("postalcode")
            country_code = j.get("country")
            if country_code == "CA":
                state = j.get("province")
            else:
                state = j.get("state")
            store_number = j.get("clientkey")
            phone = j.get("phone")
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            page_url = f"http://locations.michaels.com/{state.lower()}/{city.lower()}/{store_number}/"

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
                line = j.get(f"{day[:3]}_hrs_special")
                _tmp.append(f"{day.capitalize()}: {line}")

            hours_of_operation = ";".join(_tmp)

            if hours_of_operation.count("None") == 7:
                hours_of_operation = "Temporarily Closed"

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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.michaels.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
