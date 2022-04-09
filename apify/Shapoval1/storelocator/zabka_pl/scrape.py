from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.zabka.pl/"
    api_url = "https://www.zabka.pl/ajax/shop-clusters.json"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        store_number = j.get("id")
        latitude = j.get("lat")
        longitude = j.get("lng")
        r = session.get(
            f"https://apkykk0pza-2.algolianet.com/1/indexes/prod_locator_prod_zabka/{store_number}?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%203.22.1&x-algolia-application-id=APKYKK0PZA&x-algolia-api-key=71ca67cda813cec86431992e5e67ede2",
            headers=headers,
        )
        k = r.json()
        slug = k.get("slug")
        page_url = f"https://www.zabka.pl/znajdz-sklep/sklep/{slug}"
        street_address = k.get("address") or "<MISSING>"
        state = k.get("county") or "<MISSING>"
        postal = k.get("postcode") or "<MISSING>"
        country_code = "PL"
        city = k.get("city") or "<MISSING>"
        hours_of_operation = (
            "".join(k.get("openTime")) + " - " + "".join(k.get("closeTime"))
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=SgRecord.MISSING,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
