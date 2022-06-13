import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.cashconverters.co.nz/"
    api_url = "https://www.cashconverters.co.nz/sitemap-pages.xml"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath('//url/loc[contains(text(), "store/")]')
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        js_block = "".join(tree.xpath('//script[@type="application/ld+json"]/text()'))
        j = json.loads(js_block)
        location_name = j.get("name")
        ad = "".join(j.get("address")).replace("Henderson", ",Henderson").strip()
        street_address = ad.split(",")[0].strip()
        postal = ad.split()[-1].strip()
        country_code = "NZ"
        city = " ".join(ad.split(",")[-1].split()[:-1])
        latitude = j.get("geo").get("latitude")
        longitude = j.get("geo").get("longitude")
        phone = j.get("telephone")
        hours_of_operation = " ".join(j.get("openingHours"))
        if hours_of_operation.find("PublicHolidays") != -1:
            hours_of_operation = hours_of_operation.split("PublicHolidays")[0].strip()

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
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
