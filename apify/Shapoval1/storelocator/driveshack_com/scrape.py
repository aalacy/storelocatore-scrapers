from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.driveshack.com"
    api_url = "https://author-prod.driveshack.com/wp-json/wp/v2/cpt_location/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = j.get("link")
        location_name = j.get("title").get("rendered") or "<MISSING>"
        location_type = j.get("type") or "<MISSING>"
        ad = j.get("acf").get("hero_group").get("address")
        a = html.fromstring(ad)

        street_address = "".join(a.xpath("//p/text()[1]")).replace("\n", "").strip()
        adr = "".join(a.xpath("//p/text()[2]")).replace("\n", "").strip()
        state = adr.split(",")[1].split()[0].strip()
        postal = adr.split(",")[1].split()[1].strip()
        country_code = "US"
        city = adr.split(",")[0].strip()
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("acf").get("coordinates_group").get("latitude")
        longitude = j.get("acf").get("coordinates_group").get("longitude")
        phone = j.get("acf").get("hero_group").get("phone_number") or "<MISSING>"
        hours = j.get("acf").get("hero_group").get("hours").get("copy")
        hours_of_operation = "<MISSING>"
        if hours:
            h = html.fromstring(hours)
            hours_of_operation = (
                " ".join(h.xpath("//*//text()")).replace("\n", "").strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {adr}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
