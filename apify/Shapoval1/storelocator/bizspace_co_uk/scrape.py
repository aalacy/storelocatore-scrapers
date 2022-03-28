import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bizspace.co.uk/"
    api_url = "https://www.bizspace.co.uk/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[@data-mapid]")

    for d in div:
        slug = "".join(d.xpath("./a/@href"))
        region_page_url = f"https://www.bizspace.co.uk{slug}"
        r = session.get(region_page_url, headers=headers)
        tree = html.fromstring(r.text)

        div = tree.xpath("//div[@data-titleurl]//h3/a")
        for d in div:
            slug = "".join(d.xpath(".//@href"))
            page_url = f"https://www.bizspace.co.uk{slug}"
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            location_name = "".join(tree.xpath("//h1/text()")) or "<MISSING>"
            js_block = (
                "".join(
                    tree.xpath(
                        '//script[contains(text(), "window.__PRELOADED_STATE__")]/text()'
                    )
                )
                .split("window.__PRELOADED_STATE__ = ")[1]
                .strip()
            )
            js = json.loads(js_block)["property"]["propertyDetails"]

            a = js.get("address")
            street_address = a.get("addressLine1") or "<MISSING>"
            state = a.get("county") or "<MISSING>"
            state = str(state).strip() or "<MISSING>"
            postal = a.get("postcode") or "<MISSING>"
            country_code = "UK"
            city = a.get("city") or "<MISSING>"
            if city == "<MISSING>":
                city = a.get("town")
            if city == "<MISSING>":
                city = state
            store_number = a.get("id") or "<MISSING>"
            latitude = a.get("latitude") or "<MISSING>"
            longitude = a.get("longitude") or "<MISSING>"
            phone = js.get("phone")

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
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
