from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.oilvinegar.nl/"
    api_url = "https://www.oilvinegar.nl/rest/V1/storelocator/search/?searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bfield%5D=country_id&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bvalue%5D=NL&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bcondition_type%5D=eq&_=1652338262228"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["items"]
    for j in js:

        slug = j.get("website")
        page_url = f"https://www.oilvinegar.nl/{slug}"
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("street") or "<MISSING>"
        state = j.get("region") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country_code = "NL"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        phone = (
            "".join(
                tree.xpath(
                    '//td[./span[contains(text(), "Telefoon")]]/following-sibling::td//text()'
                )
            )
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//tr[.//span[text()="Openingstijden"]]/following-sibling::tr//td//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )

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
