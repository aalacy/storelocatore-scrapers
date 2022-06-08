from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.arwtruck.com/"
    api_url = "https://www.arwtruck.com/about-us/contact.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="dealer-info"]')
    for d in div:

        page_url = "https://www.arwtruck.com/about-us/contact.html"
        location_name = "".join(d.xpath(".//h2/text()"))
        street_address = "".join(d.xpath(".//h2/following-sibling::p[1]/text()[1]"))
        ad = (
            "".join(d.xpath(".//h2/following-sibling::p[1]/text()[2]"))
            .replace("\n", "")
            .replace("Calgary", "Calgary,")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = " ".join(ad.split(",")[1].split()[-2:])
        country_code = "CA"
        city = ad.split(",")[0].strip()
        map_link = "".join(d.xpath("./following-sibling::div[1]//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = "<MISSING>"
        ph = d.xpath(".//h2/following-sibling::p[2]/text()")
        for p in ph:
            if "Tel:" in p:
                phone = str(p).replace("\n", "").replace("Tel:", "").strip()

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
            hours_of_operation=SgRecord.MISSING,
            raw_address=street_address + " " + ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
