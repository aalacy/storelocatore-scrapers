from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api_url = "https://dotcom-location-api.dotcom-prod-ase.p.azurewebsites.net/api/mergelocations/getbygeofilterquery?latitude=44.8739807&longitude=-93.3352547&distance=5000&count=5000"
    r = session.get(api_url)
    js = r.json()["Results"]

    for s in js:
        j = s.get("BankLocation")
        a = j.get("Address")
        location_type = j.get("LocationType")
        if location_type == "ATM":
            continue
        street_address = a.get("Street")
        city = a.get("City")
        state = a.get("State")
        postal = a.get("PostalCode")
        country_code = "US"
        store_number = j.get("Id")
        page_url = f'https://www.tcfbank.com/locations/details/{j.get("FormttedUrlForDetailsPage")}'
        location_name = j.get("Name")
        phone = j.get("ExternalPhone")
        loc = j.get("Coordinates")
        latitude = loc[0]
        longitude = loc[1]
        hours_of_operation = j.get("HoursLobby")
        if page_url.find("temporarily-closed") != -1:
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
    locator_domain = "https://www.tcfbank.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
