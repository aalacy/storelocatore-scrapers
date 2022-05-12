import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://grupoojodeagua.com.mx/"
    page_url = "https://grupoojodeagua.com.mx/sucursales/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./div/div[@class="ult_expheader"]]')
    for d in div:
        state = "".join(d.xpath(".//text()")).replace("\n", "").strip()
        citites = d.xpath('.//following-sibling::div[1]//div[@class="vc_tta-panel"]')
        for c in citites:
            city = "".join(c.xpath('.//div[@class="vc_tta-panel-heading"]//h4//text()'))
            location_name = city
            info = c.xpath('.//div[@class="vc_tta-panel-body"]//*//text()')
            info = list(filter(None, [a.strip() for a in info]))
            ad = " ".join(info).split("DIRECCIÓN")[1].strip()
            if ad.find("Tel") != -1:
                ad = ad.split("Tel")[0].strip()
            if ad.find("TEL") != -1:
                ad = ad.split("TEL")[0].strip()
            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            postal = a.postcode or "<MISSING>"
            postal = (
                str(postal).replace(".", "").replace("C", "").replace("P", "").strip()
            )
            country_code = "MX"
            if state == "FL":
                country_code = "US"
            text = "".join(c.xpath('.//a[contains(@href, "maps")]/@href'))
            try:
                if text.find("ll=") != -1:
                    latitude = text.split("ll=")[1].split(",")[0]
                    longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
                else:
                    latitude = text.split("@")[1].split(",")[0]
                    longitude = text.split("@")[1].split(",")[1]
            except IndexError:
                latitude, longitude = "<MISSING>", "<MISSING>"
            info_for_phone = " ".join(info)
            ph = (
                re.findall(
                    r"(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})",
                    info_for_phone,
                )
                or "<MISSING>"
            )

            phone = "<MISSING>"
            if ph != "<MISSING>":
                phone = "".join(ph[0]).strip()
            if phone == "<MISSING>":
                phone = (
                    " ".join(
                        c.xpath(
                            './/*[contains(text(), "Tel.")]//text() | .//span[contains(text(), "TEL.")]/text()[1]'
                        )
                    )
                    .replace("\n", "")
                    .replace("Tel.", "")
                    .replace("TEL.", "")
                    .strip()
                    or "<MISSING>"
                )
            hours_of_operation = " ".join(info).split("HORARIO")[1].strip()
            if hours_of_operation.find("Facturación") != -1:
                hours_of_operation = hours_of_operation.split("Facturación")[0].strip()
            if hours_of_operation.find("DIRECCIÓN") != -1:
                hours_of_operation = hours_of_operation.split("DIRECCIÓN")[0].strip()

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
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
