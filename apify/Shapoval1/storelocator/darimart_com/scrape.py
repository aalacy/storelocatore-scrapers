from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.darimart.com"
    api_url = "https://www.darimart.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = "".join(
        tree.xpath('//script[contains(text(), "mapboxgl.accessToken")]/text()')
    ).split(".setHTML(")

    for d in div:
        latitude = d.split(".setLngLat([")[-1].split(",")[1].split("]")[0].strip()
        longitude = d.split(".setLngLat([")[-1].split(",")[0].strip()

        ad = d.split(");")[0].strip()
        if ad.find("<p>") == -1:
            continue
        a = html.fromstring(ad)
        csz = (
            " ".join(a.xpath("//p/strong/following-sibling::text()[1]"))
            .replace("\r\n", "")
            .replace("35831 Hwy 58", "")
            .strip()
        )
        if csz == "Mon-Th 5:30am-10pm":
            csz = "<MISSING>"
        page_url = "https://www.darimart.com/locations/"
        street_address = "".join(a.xpath("//*/strong[1]/text()"))
        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "US"
        city = "<MISSING>"
        phone = "".join(a.xpath('//a[contains(@href, "tel")]/text()'))
        if csz != "<MISSING>":
            state = csz.split(",")[1].split()[0].strip()
            postal = csz.split(",")[1].split()[-1].strip()
            city = csz.split(",")[0].strip()
        try:
            store_number = street_address.split("#")[1].strip()
        except:
            store_number = "<MISSING>"
        hours_of_operation = (
            " ".join(
                a.xpath(
                    '//*[contains(text(), "pm")]/text() | //*[contains(text(), "am-")]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=SgRecord.MISSING,
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
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
