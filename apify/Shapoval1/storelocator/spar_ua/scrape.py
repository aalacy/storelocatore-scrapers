from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://spar.ua"
    api_url = "https://spar.ua/shops"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//li[@class="li-shop"]')
    for d in div:
        slug = "".join(d.xpath(".//a/@data-id"))
        street_address = "".join(
            d.xpath('.//a[@class="select-shop"]/span[@class="street"][2]/text()')
        )
        state = "".join(
            d.xpath('.//a[@class="select-shop"]/span[@class="street"][1]/text()')
        )
        country_code = "UA"
        city = "".join(d.xpath('.//span[@class="citi"]/text()')) or "<MISSING>"

        r = session.get(f"https://spar.ua/shop/list/1?id={slug}", headers=headers)
        js = r.json()
        for j in js:
            page_url = "https://spar.ua/shops"
            map_link = "".join(j.get("map"))
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
            phone = j.get("tel") or "<MISSING>"
            hours_of_operation = j.get("schedule") or "<MISSING>"

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=SgRecord.MISSING,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=SgRecord.MISSING,
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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
