from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.pizzacapers.com.au/"
    api_url = "https://www.pizzacapers.com.au/stores/stores_for_map_markers.json/?catering_active=undefined"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        page_id = j.get("id")
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("address") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postcode") or "<MISSING>"
        country_code = "US"
        city = j.get("suburb") or "<MISSING>"
        ll = str(j.get("location"))
        latitude = ll.split(",")[0].strip()
        longitude = ll.split(",")[1].strip()
        r = session.get(
            f"https://www.pizzacapers.com.au/stores/{page_id}/store_online/?&context=locator"
        )
        tree = html.fromstring(r.text)
        slug = "".join(tree.xpath("//h4[./a]/a/@href"))
        page_url = f"https://www.pizzacapers.com.au{slug}"
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()')) or "<MISSING>"
        _tmp = []
        days = tree.xpath(
            '//h4[text()="Opening Hours"]/following-sibling::table//tr/td[1]/text()'
        )
        times = tree.xpath(
            '//h4[text()="Opening Hours"]/following-sibling::table//tr/td[2]/text()'
        )

        for d, l in zip(days, times):
            _tmp.append(f"{str(d).split(',')[0].strip()}: {l.strip()}")
        hours_of_operation = "; ".join(_tmp)

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
