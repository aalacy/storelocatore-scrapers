from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://www.breezethru.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./h3[contains(text(), "Store")]]')
    for d in div:

        page_url = "https://www.breezethru.com/locations"
        location_name = (
            "".join(d.xpath(".//h3/text()")).replace("★", "").replace("✭", "").strip()
        )
        street_address = (
            "".join(d.xpath(".//p[1]/a/text()[1]")).replace("\n", "").strip()
        )
        ad = "".join(d.xpath(".//p[1]/a/text()[2]")).replace("\n", "").strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "USA"
        city = ad.split(",")[0].strip()
        store_number = location_name.split("#")[1].strip()
        latitude = (
            "".join(d.xpath(".//preceding::div/@data-block-json"))
            .split(f"{store_number}")[1]
            .split(",")[-3]
            .strip()
        )
        longitude = (
            "".join(d.xpath(".//preceding::div/@data-block-json"))
            .split(f"{store_number}")[1]
            .split(",")[-2]
            .strip()
        )
        phone = "".join(d.xpath(".//p[2]/a/text()"))

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
    locator_domain = "https://www.breezethru.com"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
