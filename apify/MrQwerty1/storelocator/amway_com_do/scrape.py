from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    for i in range(100):
        api = f"https://www.amway.com.do/en_DO/store-finder?q=&page={i}&gpsAvailable=false"
        r = session.get(api)
        js = r.json()["data"]

        for j in js:
            location_name = j.get("name")
            latitude = j.get("latitude")
            longitude = j.get("longitude")

            _tmp = []
            days = {
                "0": "Sunday",
                "1": "Monday",
                "2": "Tuesday",
                "3": "Wednesday",
                "4": "Thursday",
                "5": "Friday",
                "6": "Saturday",
            }
            hours = j.get("openings") or {}
            for k, v in hours.items():
                day = days.get(k)
                _tmp.append(f"{day}: {v}")
            hours_of_operation = ";".join(_tmp)

            phone = j.get("phone") or ""
            if "e" in phone:
                phone = phone.split("e")[0].strip()
            street_address = f'{j.get("line1")} {j.get("line2") or ""}'.strip()
            city = j.get("town")
            state = j.get("state")
            postal = j.get("postalCode")

            row = SgRecord(
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="DO",
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        if len(js) < 10:
            break


if __name__ == "__main__":
    locator_domain = "https://www.amway.com.do/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
