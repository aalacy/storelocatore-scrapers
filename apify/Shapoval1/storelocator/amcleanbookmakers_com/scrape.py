import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.amcleanbookmakers.com/"
    page_url = "https://www.amcleanbookmakers.com/list-of-betting-offices/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="shop"]')
    for d in div:

        location_name = "".join(d.xpath(".//h3/text()")).strip()
        street_address = (
            "".join(d.xpath(".//ul/li[1]/text()"))
            .replace("\n", "")
            .replace("’", "'")
            .strip()
        )
        city = "".join(d.xpath(".//ul/li[last() - 1]/text()")).replace("\n", "").strip()
        postal = "".join(d.xpath(".//ul/li[last()]/text()")).replace("\n", "").strip()
        country_code = "UK"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        js_block = (
            "".join(tree.xpath('//script[contains(text(), "pois")]/text()'))
            .split('"pois":')[1]
            .split("} );")[0]
            .strip()
        )
        js = json.loads(js_block)

        for j in js:
            ad = (
                "".join(j.get("address"))
                .replace("\n", " ")
                .replace("\r", " ")
                .replace("140 Petershill", "140 Peter's Hill")
                .replace(
                    "Unit 20, Kings Square Shopping Centre",
                    "Unit 20, King's Square Shopping Centre",
                )
                .replace("117 Crumlin Road", "177 Crumlin Road")
                .replace("37 Holywoord Road", "37 Holywood Road")
                .replace("430 Newtownards Raoad", "430 Newtownards Road")
                .replace("155 Cormac Street", "155 Cromac Street")
                .strip()
            )
            if ad.find(f"{street_address}") != -1:
                latitude = j.get("point").get("lat")
                longitude = j.get("point").get("lng")

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
            raw_address=f"{street_address} {city}, {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
