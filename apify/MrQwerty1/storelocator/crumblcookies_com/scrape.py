from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://crumblcookies.com/_next/data/iOdOKVl83Kyq3BxF70cOQ/en/stores.json"
    r = session.get(api, headers=headers)
    js = r.json()["pageProps"]["stores"]

    for j in js:
        raw_address = j.get("address") or ""
        city = j.get("city") or ""
        state = j.get("state")
        postal = raw_address.split()[-1]
        street_address = raw_address.split(f", {city}")[0]
        if postal in street_address:
            street_address = street_address.split(city)[0].strip()

        country_code = "US"
        location_name = j.get("name")
        slug = j.get("slug")
        page_url = f"{locator_domain}{slug}"
        phone = j.get("phone") or ""
        phone = phone.replace("`", "").strip()
        if ":" in phone:
            phone = phone.split(":")[-1].strip()
        if "moore" in phone:
            phone = phone.split("moore")[0].strip()
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        try:
            hours_of_operation = j["storeHours"]["description"]
        except KeyError:
            hours_of_operation = SgRecord.MISSING

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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://crumblcookies.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
