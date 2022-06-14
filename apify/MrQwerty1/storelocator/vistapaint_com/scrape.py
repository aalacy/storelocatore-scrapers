from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api_url = "https://vistapaint.com/stores"

    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//table[@class="table table-striped table-condensed table-bordered"]//tr[./td]'
    )
    for d in div:
        slug = "".join(d.xpath("./td[1]/a/@href"))
        page_url = f"https://vistapaint.com{slug}"
        street_address = "".join(d.xpath("./td[2]/text()"))
        state = "".join(d.xpath("./td[3]/text()")).strip()
        postal = "".join(d.xpath("./td[4]/text()")).strip()
        country_code = "US"
        if "Zhejiang" in state:
            country_code = "CH"
        if "China" in postal:
            postal = SgRecord.MISSING
        city = "".join(d.xpath("./td[1]/a/text()"))
        if city.find("/") != -1:
            city = city.split("/")[0].strip()
        if city.find("(") != -1:
            city = city.split("(")[0].strip()
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
        store_number = page_url.split("/")[-1].strip()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(tree.xpath("//h2/text()"))
        hours_of_operation = (
            " ".join(tree.xpath('//table[@class="table table-condensed"]//text()'))
            .replace("\n", "")
            .split("Store_Hours:")[1]
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation == "Mon-Fri Saturday Sunday":
            hours_of_operation = SgRecord.MISSING

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {state} {postal}".replace(
                "<MISSING>", ""
            ).strip(),
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://vistapaint.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
