from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://workplaceone.com/"
    api_url = "https://workplaceone.com/page-data/locations/page-data.json"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["result"]["data"]["cms"]["locations"]
    for j in js:
        slug = j.get("slug")
        page_url = f"https://workplaceone.com/locations/{slug}"
        location_name = j.get("title")
        country_code = "CA"
        city = j.get("location").get("parts").get("city")
        store_number = j.get("id")
        latitude = j.get("location").get("lat")
        longitude = j.get("location").get("lng")
        r = session.get(
            f"https://workplaceone.com/page-data/locations/{slug}/page-data.json",
            headers=headers,
        )
        s_js = r.json()["result"]["pageContext"]["data"]
        adr = "".join(s_js.get("mapAddress")).replace("ON,", "ON")
        street_address = "".join(adr.split(",")[:-2])
        state = adr.split(",")[-1].split()[0].strip()
        postal = " ".join(adr.split(",")[-1].split()[1:])
        phone = s_js.get("phoneNumber")[0].get("withStyles")

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
            hours_of_operation=SgRecord.MISSING,
            raw_address=adr,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
