from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    apis = [
        "https://www.firsthorizon.com/api/locations/branches",
        "https://www.firsthorizon.com/api/locations/atms",
    ]
    data = {
        "Latitude": "33.5178769",
        "Longitude": "-86.8094808",
        "SearchRadiusInMiles": "5000",
    }

    for api in apis:
        r = session.post(api, headers=headers, data=data)
        if "branch" in api:
            location_type = "Branch"
            js = r.json()["Branches"]
        else:
            location_type = "ATM"
            js = r.json()["ATMs"]

        for j in js:
            street_address = j.get("Street")
            city = j.get("City")
            state = j.get("State")
            postal = j.get("Zip")
            raw_address = f"{street_address}, {city}, {state} {postal}"
            country_code = "US"
            store_number = j.get("id")
            location_name = j.get("Name")
            phone = j.get("Phone")
            latitude = j.get("Lat")
            longitude = j.get("Lng")

            _tmp = []
            hours = j.get("Hours") or []
            for h in hours:
                day = h.get("Day")
                inter = h.get("Time")
                _tmp.append(f"{day}: {inter}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                store_number=store_number,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.firsthorizon.com/"
    page_url = "https://www.firsthorizon.com/Support/Contact-Us/Location-Listing"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.firsthorizon.com/Support/Contact-Us?lf-location=35203&lf-location-type=branch",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.firsthorizon.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_TYPE})
        )
    ) as writer:
        fetch_data(writer)
