from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://maps.castrol.com/api/v1/client/search?countries=1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66&filters[]=16&lat=33.0218117&lng=-97.12516989999999"
    r = session.get(api, headers=headers)
    js = r.json()["data"]

    for j in js:
        raw_address = str(j.get("formatted_address")).replace("\n", " ")
        adr = str(j.get("formatted_address")).split("\n")
        street_address = adr.pop(0).replace(",", "").strip()
        city = adr.pop(0).replace(",", "").strip()
        state = adr.pop(0)
        postal = adr.pop(0)
        country_code = j.get("country")
        store_number = j.get("id")
        location_name = j.get("name")
        page_url = f"https://maps.castrol.com/{store_number}"
        phone = j.get("telephone_number")
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
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "http://www.castrolpremiumlube.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
