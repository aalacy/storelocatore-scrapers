from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.johnsonfitness.com.au/"
    api_url = "https://www.johnsonfitness.com.au/pages/contact-us"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    page_url = "https://www.johnsonfitness.com.au/pages/contact-us"
    location_name = "".join(tree.xpath('//meta[@property="og:site_name"]/@content'))

    ad = (
        "".join(tree.xpath('//div[@class="rte appear-delay-2"]/p[1]/text()'))
        .replace("\n", "")
        .strip()
    )

    street_address = ad.split(",")[0].strip()
    state = ad.split()[-2].strip()
    postal = ad.split()[-1].strip()
    country_code = "AU"
    city = " ".join(ad.split(",")[1].split()[:-2]).strip()
    phone = (
        "".join(tree.xpath('//p[./strong[contains(text(), "Sales")]]/text()[1]'))
        .replace("\n", "")
        .strip()
    )
    hours_of_operation = (
        " ".join(tree.xpath('//div[@class="rte appear-delay-2"]/p[2]/text()'))
        .replace("\n", "")
        .strip()
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
        latitude=SgRecord.MISSING,
        longitude=SgRecord.MISSING,
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
