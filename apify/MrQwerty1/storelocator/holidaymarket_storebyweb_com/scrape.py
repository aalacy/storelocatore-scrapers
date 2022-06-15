from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://holidaymarket.storebyweb.com/s/1000-28/api/stores"
    r = session.get(api, headers=headers)
    js = r.json()["data"]

    for j in js:
        try:
            a = j['addresses'][0]
        except:
            a = dict()

        adr1 = a.get("street1") or ""
        adr2 = a.get("street2") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = a.get("city")
        state = a.get("state")
        postal = a.get("postal")
        country_code = a.get('country')
        store_number = j.get("id")
        location_name = j.get('name')
        phone = j['phones'][0]['phone']
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
    locator_domain = "https://holidaymarket.storebyweb.com/"
    page_url = 'https://holidaymarket.storebyweb.com/s/1000-28/select-store'
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
