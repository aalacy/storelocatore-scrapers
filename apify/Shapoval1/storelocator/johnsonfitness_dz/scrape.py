from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "http://johnsonfitness.dz/"
    api_url = "http://johnsonfitness.dz/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    page_url = "http://johnsonfitness.dz/"
    street_address = (
        "".join(
            tree.xpath(
                '//img[contains(@src, "localisation2")]/following-sibling::text()[1]'
            )
        )
        .replace("\n", "")
        .replace("Adresse :", "")
        .replace("\r", "")
        .strip()
    )
    ad = (
        "".join(
            tree.xpath(
                '//img[contains(@src, "localisation2")]/following-sibling::text()[2]'
            )
        )
        .replace("\n", "")
        .replace("\r", "")
        .strip()
    )
    state = ad.split(",")[0].split()[-1].strip()
    country_code = ad.split(",")[1].strip()
    city = " ".join(ad.split(",")[0].split()[:-1])
    map_link = "".join(tree.xpath("//iframe/@src"))
    latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
    longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    phone = (
        "".join(
            tree.xpath('//img[contains(@src, "appel2")]/following-sibling::text()[1]')
        )
        .replace("\n", "")
        .replace("Office :", "")
        .strip()
    )

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
        hours_of_operation=SgRecord.MISSING,
        raw_address=f"{street_address} {ad}",
    )

    sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
