import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.nocibe.fr/parfumeries"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text.replace(":stores", "stores"))
    text = "".join(tree.xpath("//*[@stores]/@stores"))
    js = json.loads(text)

    for jj in js.values():
        for j in jj:
            adr1 = j.get("adressLine1") or ""
            adr2 = j.get("adressLine2") or ""
            street_address = f"{adr1} {adr2}".strip()
            city = j.get("city")
            state = j.get("State")
            postal = j.get("zipCode")
            country_code = "FR"
            store_number = j.get("storeId")
            location_name = j.get("storeName")
            slug = j.get("storeNameForUrl")
            page_url = f"https://www.nocibe.fr{slug}"
            phone = j.get("phone1")
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            hours_of_operation = str(j.get("horairesHtml") or "").replace("<br/>", ";")

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
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.nocibe.fr/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
