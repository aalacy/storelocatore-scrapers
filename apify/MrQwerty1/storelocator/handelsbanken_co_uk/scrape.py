import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    countries = ["se", "dk", "fi", "nl", "no", "gb", "fr", "lu"]
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    for country in countries:
        locator_domain = f"https://www.handelsbanken.{country}/"
        api = f"https://locator.maptoweb.dk/handelsbanken.com/locator/points/where/CountryCode/eqi/{country}"
        r = session.get(api, headers=headers)
        js = r.json()["results"]

        for j in js:
            location_name = j.get("name")
            page_url = j.get("url")
            street_address = j.get("streetName") or ""
            street_address = street_address.replace("&#8217;", "'")
            city = j.get("cityName")
            state = j.get("countryState")
            postal = j.get("zipCode")
            country_code = j.get("countryCode")

            phone = j.get("phone")
            loc = j.get("location") or {}
            latitude = loc.get("lat")
            longitude = loc.get("lng")

            hours_of_operation = SgRecord.MISSING
            location_type = SgRecord.MISSING
            store_number = SgRecord.MISSING
            options = j.get("options") or []
            for o in options:
                if o.get("name") == "LocationType":
                    location_type = o.get("value")
                if o.get("name") == "BranchId":
                    store_number = o.get("value")
                if o.get("name") == "OpenHoursSpan":
                    text = o.get("value")
                    _tmp = []
                    hours = json.loads(text)
                    for h in hours:
                        day = days[int(h.get("Weekday"))]
                        start = h.get("Open")
                        end = h.get("Close")
                        if start:
                            _tmp.append(f"{day}: {start}-{end}")
                    hours_of_operation = ";".join(_tmp)

            if country_code == "FR":
                page_url = (
                    "https://www.handelsbanken.com/en/about-the-group/locations/france"
                )
            elif country_code == "LU":
                page_url = "https://www.handelsbanken.com/en/about-the-group/locations/luxembourg"

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=store_number,
                location_type=location_type,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_TYPE}
            )
        )
    ) as writer:
        fetch_data(writer)
