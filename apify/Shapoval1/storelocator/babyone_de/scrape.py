import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.babyone.de/"
    api_url = "https://www.babyone.de/Fachm%C3%A4rkte"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    js_block = "".join(tree.xpath('//div[@id="jsonstores"]/@data-stores'))
    js = json.loads(js_block)
    for j in js["stores"]:

        location_name = j.get("name") or "<MISSING>"
        street_address = (
            f"{j.get('address1')} {j.get('address2') or ''}".replace("None", "").strip()
            or "<MISSING>"
        )
        postal = j.get("postalCode") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        store_number = j.get("ID") or "<MISSING>"
        page_url = f"https://www.babyone.de/Fachmarkt?StoreID={store_number}"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        country_code = "".join(tree.xpath("//div/@data-country")) or "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[@class="nsd-openinghours-content"]/div/p[contains(text(), "Mo")]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//div[@class="nsd-openinghours-content"]/div/text()[1] | //div[@class="nsd-openinghours-content"]/div/p[1]/text()[2]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        cls = "".join(tree.xpath('//*[contains(text(), "geschlossen")]/text()'))
        if cls:
            hours_of_operation = "Closed"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
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
