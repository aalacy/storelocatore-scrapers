from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.goldennozzlecarwash.com"
    api_url = "https://www.goldennozzlecarwash.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./div/div/div/h2/a[contains(@href, "tel")]]')
    for d in div:

        page_url = "https://www.goldennozzlecarwash.com/locations/"
        street_address = " ".join(d.xpath("./div[2]//text()")).replace("\n", "").strip()
        street_address = " ".join(street_address.split())
        state = "".join(d.xpath('./preceding::h1[contains(text(), "(")][1]/text()'))
        if state.find("(") != -1:
            state = state.split("(")[0].strip()
        country_code = "US"
        city = "".join(d.xpath(".//h1//text()"))
        phone = "".join(d.xpath("./div[3]//text()")).replace("\n", "").strip()
        info = d.xpath(".//*//text()")
        info = list(filter(None, [a.strip() for a in info]))
        location_name = f"Golden Nozzle {city}"
        tmp = []
        for i in info:
            if "PM" in i:
                tmp.append(i)
        hours_of_operation = (
            "; ".join(tmp)
            .replace("; Open 8AM-5PM every day.", "")
            .replace("; 8AM-7PM Every day", "")
            .strip()
        )
        if hours_of_operation.find("; Mon") != -1:
            hours_of_operation = hours_of_operation.split("; Mon")[0].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
