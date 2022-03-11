from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://wirelessplus.com"
    api_url = "https://wirelessplus.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./h3]")
    for d in div:

        page_url = "https://wirelessplus.com/locations/"
        location_name = "".join(d.xpath(".//h3/text()")).strip() or "<MISSING>"
        if location_name == "<MISSING>":
            continue
        street_address = (
            "".join(d.xpath('.//p[@class="gbcols_p"]/text()[1]'))
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(d.xpath('.//p[@class="gbcols_p"]/text()[2]'))
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].strip()
        postal = ad.split(",")[2].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        phone = (
            "".join(d.xpath('.//p[@class="gbcols_p"]/text()[3]'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/preceding::h2[text()="Hours of Operation"]/following-sibling::div/text()'
                )
            )
            .replace("\r\n", "")
            .strip()
        )

        session = SgRequests()
        r = session.get(
            "https://wirelessplus.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABU0Wug",
            headers=headers,
        )
        js = r.json()["markers"]
        for j in js:
            title = "".join(j.get("title"))
            if title == "DTLA - E. 2nd St.":
                title = "DTLA - Wakaba"
            if title == "La Cañada":
                title = "La Canada"
            if title.find(f"{location_name}") != -1:
                latitude = j.get("lat")
                longitude = j.get("lng")

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
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
