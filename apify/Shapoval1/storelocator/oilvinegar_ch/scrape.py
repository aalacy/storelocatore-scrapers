from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.oilvinegar.ch/"
    api_url = "https://www.oilvinegar.ch/rest/V1/storelocator/search/?searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bfield%5D=country_id&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bvalue%5D=CH&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bcondition_type%5D=eq&_=1652339002942"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["items"]
    for j in js:

        slug = j.get("website")
        page_url = f"https://www.oilvinegar.ch/{slug}"
        if not slug:
            page_url = "https://www.oilvinegar.ch/dealers/"

        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("street") or "<MISSING>"
        state = j.get("region") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country_code = "CH"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        if page_url != "https://www.oilvinegar.ch/dealers/":
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            phone = (
                "".join(
                    tree.xpath(
                        '//h3[contains(text(), "Telefon")]/following-sibling::div[1]//text()'
                    )
                )
                or "<MISSING>"
            )
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//h4[contains(text(), "Öffnungszeiten")]/following-sibling::div[1]//text()'
                    )
                )
                .replace("\n", "")
                .replace("\r", "")
                .strip()
                or "<MISSING>"
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
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
