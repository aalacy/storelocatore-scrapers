from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.curveskorea.co.kr"
    api_url = "https://www.curveskorea.co.kr/club-locator/search.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//h4[text()="시/도 선택"]/following-sibling::div[@class="set_view"]/a'
    )
    for d in div:
        state_id = "".join(d.xpath(".//@id"))
        state = "".join(d.xpath(".//@title"))
        r_1 = session.get(
            f"https://www.curveskorea.co.kr/club-locator/_php/si_do_ajax.php?sido={state_id}"
        )
        tree_1 = html.fromstring(r_1.text)
        div_1 = tree_1.xpath("//a")
        for d_1 in div_1:
            city = "".join(d_1.xpath(".//@title"))
            r_2 = session.get(
                f"https://www.curveskorea.co.kr/club-locator/_php/si_do_ajax.php?gungu_name={city}&sido_name={state}"
            )
            tree_2 = html.fromstring(r_2.text)
            div_2 = tree_2.xpath('//a[@class="sch_result"]')
            for d_2 in div_2:
                location_name = "".join(d_2.xpath(".//@title"))
                page_id = "".join(d_2.xpath(".//@id"))
                page_url = "https://www.curveskorea.co.kr/club-locator/search.html"
                street_address = "".join(d_2.xpath('.//span[@class="addr"]/text()[1]'))
                country_code = "KR"
                phone = (
                    "".join(d_2.xpath('.//span[@class="addr"]/text()[2]'))
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
                if phone == "--":
                    phone = "<MISSING>"
                r_3 = session.get(
                    f"https://www.curveskorea.co.kr/club-locator/_php/si_do_ajax.php?shop_idx={page_id}"
                )
                tree_3 = html.fromstring(r_3.text)
                latitude = "".join(tree_3.xpath('//input[@name="x"]/@value'))
                longitude = "".join(tree_3.xpath('//input[@name="y"]/@value'))

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
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=SgRecord.MISSING,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
