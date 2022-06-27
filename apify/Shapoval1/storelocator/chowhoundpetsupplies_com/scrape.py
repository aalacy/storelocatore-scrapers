import httpx
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://chowhoundpetsupplies.com/"
    api_url = "https://chowhoundpetsupplies.com/store-locator/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    with SgRequests() as http:
        r = http.get(url=api_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath('//a[contains(text(), "Details")]')
        for d in div:

            page_url = "".join(d.xpath(".//@href"))
            r = http.get(url=page_url, headers=headers)
            assert isinstance(r, httpx.Response)
            assert 200 == r.status_code
            tree = html.fromstring(r.text)

            location_name = "".join(tree.xpath("//h4//text()")) or "<MISSING>"
            ad = (
                "".join(tree.xpath("//h4/following-sibling::p[1]/text()[1]"))
                .replace("\n", "")
                .strip()
            )
            a = parse_address(USA_Best_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "US"
            city = a.city or "<MISSING>"
            map_link = "".join(tree.xpath("//iframe/@src"))
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
            phone = (
                "".join(tree.xpath("//h4/following-sibling::p[1]/text()[2]"))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//li[./b[contains(text(), "Store Hours:")]]/following-sibling::li//text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
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
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
