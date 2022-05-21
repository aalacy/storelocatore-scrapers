from lxml import html, etree
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//table//tr")
    divs.pop(0)

    for d in divs:
        if len(d.xpath("./td")) == 6:
            et = etree.XML(html.tostring(d))
            td = et.xpath('.//td[contains(text(), "30770")]')[0]
            new_td = td.getparent()
            new_td.insert(new_td.index(td), etree.XML("<td>Super Mza 51</td>"))
            d = new_td

        store_number = "".join(d.xpath("./td[1]/text()")).strip()
        location_name = "".join(d.xpath("./td[2]/text()")).strip()
        street_address = "".join(d.xpath("./td[3]/text()")).strip()
        postal = "".join(d.xpath("./td[5]/text()")).strip()
        cs = "".join(d.xpath("./td[6]/text()")).strip().split(",")
        city = cs.pop(0)
        state = cs.pop()
        try:
            phone = d.xpath("./td[7]/text()")[0].strip()
            if "//" in phone:
                phone = phone.split("//")[0].strip()
        except IndexError:
            phone = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="MX",
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://pirma.com.mx/"
    page_url = "https://pirma.com.mx/pages/tiendas-fisicas"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
