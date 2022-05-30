import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://gorjana.com/"
    api_url = "https://gorjana.com/pages/store-locator"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[@class="stores stores_desktop"]/div[@class="store"]/span[@class="store__title title-medium"]/a'
    )
    for d in div:

        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://gorjana.com{slug}"
        location_name = "".join(d.xpath(".//text()")).replace("\n", "").strip()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        info = tree.xpath(
            '//div[@class="elm text-edit gf-elm-left gf-elm-center-lg gf-elm-center-md gf-elm-center-sm gf-elm-center-xs"]//text() | //div[@class="elm text-edit gf-elm-center-lg gf-elm-center-md gf-elm-center-sm gf-elm-center-xs gf-elm-center"]//text()'
        )
        info = list(filter(None, [a.strip() for a in info]))
        adr = " ".join(info)
        ad_info = tree.xpath("//div[./b]//text()")
        if not ad_info:
            ad_info = tree.xpath("//div[./strong]//text()")
        ad_info = list(filter(None, [a.strip() for a in ad_info]))
        raw_address = " ".join(ad_info)
        a = parse_address(International_Parser(), raw_address)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        if city == "<MISSING>":
            city = location_name.split(",")[0].strip()
        ph = (
            re.findall(r"[(][\d]{3}[)][ ]?[\d]{3}-[\d]{4}", adr)
            or re.findall(r"[\d]{3}-[\d]{3}-[\d]{4}", adr)
            or "<MISSING>"
        )
        phone = "".join(ph)
        hours_of_operation = "<MISSING>"
        tmp = []
        for i in info:
            if "PM" in i or "Mon-" in i or "Sun" in i:
                tmp.append(i)
            hours_of_operation = (
                "; ".join(tmp).replace(":;", ":").strip() or "<MISSING>"
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
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
