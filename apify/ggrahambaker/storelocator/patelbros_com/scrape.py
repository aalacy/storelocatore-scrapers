from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.patelbros.com/"
    api_url = "https://www.patelbros.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=&t=1629474237111"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath("//store/item")
    for d in div:
        ad = (
            " ".join(d.xpath(".//address/text()"))
            .replace("\n", "")
            .replace("&#44;", ",")
            .strip()
        )
        page_url = "".join(d.xpath(".//exturl/text()"))
        location_name = "".join(d.xpath(".//location/text()"))
        street_address = ad.split("<br />")[0].strip()
        csz = ad.split("<br />")[1].strip()
        state = " ".join(csz.split(",")[1].split()[:-1]).strip()
        postal = csz.split(",")[1].split()[-1].strip()
        country_code = "US"
        city = csz.split(",")[0].strip()
        store_number = "".join(d.xpath(".//sortord/text()"))
        latitude = "".join(d.xpath(".//latitude/text()"))
        longitude = "".join(d.xpath(".//longitude/text()"))
        phone = "".join(d.xpath(".//telephone/text()"))

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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
