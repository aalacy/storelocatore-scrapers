from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.cashconverters.sg/"
    page_url = "https://www.cashconverters.sg/pages/our-stores"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="rte"]/p[./span[not(contains(@style,"color: #"))]]')
    for d in div:

        location_name = "".join(d.xpath("./span[1]//text()"))
        ad = (
            "".join(
                d.xpath(
                    "./span[1]/following-sibling::text()[1] | ./span[1]/following-sibling::span[1]/text()"
                )
            )
            .replace("\n", "")
            .strip()
        )
        street_address = " ".join(ad.split()[:-2]).replace(",", "").strip()
        state = "<MISSING>"
        postal = ad.split()[-1].strip()
        country_code = "SG"
        city = ad.split()[-2].strip()
        info = d.xpath(".//text()")
        info = list(filter(None, [a.strip() for a in info]))
        str_info = " ".join(info)
        phone = str_info.split("Phone Number:")[1].strip()
        if phone.find("WhatsApp") != -1:
            phone = phone.split("WhatsApp")[0].strip()
        if phone.find("Fax") != -1:
            phone = phone.split("Fax")[0].strip()
        hours_of_operation = str_info.split("Opening Hours:")[1].strip()

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
