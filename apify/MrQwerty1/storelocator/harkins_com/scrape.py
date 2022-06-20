from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://cms.harkins.com/api/v1/theaters"
    r = session.get(api, headers=headers)
    js = r.json()

    for jj in js:
        for j in jj["theatres"]:
            a = j["address_lines"][0]
            street_address = a.get("address")
            city = a.get("city")
            state = a.get("state")
            postal = a.get("zip")
            country_code = "US"
            store_number = j.get("id")
            location_name = j.get("name")
            slug = j.get("slugUrl")
            page_url = f"https://www.harkins.com/theatres/{slug}"
            phone = j.get("phone")
            latitude = j.get("latitude")
            longitude = j.get("longitude")

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
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.harkins.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
