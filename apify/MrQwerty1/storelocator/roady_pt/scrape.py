import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    text = "".join(tree.xpath("//script[contains(text(), 'var handover =')]/text()"))
    text = text.split('"districts":')[1].split("}]}]}}")[0] + "}]}]"
    js = json.loads(text)

    for jj in js:
        state = jj.get("name") or ""
        stores = jj.get("store") or []

        for j in stores:
            adr = j.get("address") or "<html>"
            root = html.fromstring(adr)
            raw_address = " ".join(" ".join(root.xpath("./text()")).split())
            city = j.get("locality") or ""
            postal = j.get("postal_code") or ""
            street_address = raw_address.split(postal)[0].replace("–", " ").strip()
            country_code = "PT"
            store_number = j.get("id")
            location_name = j.get("name")
            phone = j.get("phone_number")
            latitude = j.get("lat")
            longitude = j.get("lng")

            hours = j.get("schedule") or ""
            hours_of_operation = (
                hours.replace("\r\n", "").replace("<br>", ";").replace(";;", ";")
            )

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
                raw_address=raw_address,
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.roady.pt/"
    page_url = "https://www.roady.pt/lojas"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
