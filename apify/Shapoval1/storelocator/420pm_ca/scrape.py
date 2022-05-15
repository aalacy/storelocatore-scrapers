from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.420pm.ca/"
    api_url = "https://api.storepoint.co/v1/161aa4f8605b01/locations?lat=51.0461&long=-114.0655&radius=2500000"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["results"]["locations"]
    for j in js:

        page_url = j.get("website")
        location_name = j.get("name")
        ad = "".join(j.get("streetaddress"))
        street_address = "".join(ad.split(",")[:-3]).strip()
        state = ad.split(",")[-2].split()[0].strip()
        postal = " ".join(ad.split(",")[-2].split()[1:]).strip()
        country_code = ad.split(",")[-1].strip()
        city = ad.split(",")[-3].strip()
        store_number = j.get("id")
        latitude = j.get("loc_lat")
        longitude = j.get("loc_long")
        phone = j.get("phone")
        desc = j.get("description")
        hours_of_operation = f"Monday {j.get('monday')} Tuesday {j.get('tuesday')} Wednesday {j.get('wednesday')} Thursday {j.get('thursday')} Friday {j.get('friday')} Saturday {j.get('saturday')} Sunday {j.get('sunday')}"
        if desc == "Coming Soon":
            hours_of_operation = "Coming Soon"

        row = SgRecord(
            locator_domain=locator_domain,
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
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
