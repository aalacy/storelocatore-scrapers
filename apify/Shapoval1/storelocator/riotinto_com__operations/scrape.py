import httpx
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):
    with SgRequests() as http:
        locator_domain = "https://www.riotinto.com"
        api_url = "https://www.riotinto.com/footer/contact/operations"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = http.get(url=api_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="rt-content-card rt-content-card--contact"]')
        for d in div:

            page_url = "https://www.riotinto.com/footer/contact/operations"
            location_name = "".join(
                d.xpath('.//h3[@class="rt-content-card__title field-title"]/text()')
            )
            ad = " ".join(d.xpath("./div[2]/p[1]/text()")).replace("\n", "").strip()
            ad = " ".join(ad.split())
            if ad.find("T:") != -1:
                ad = ad.split("T:")[0].strip()

            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "".join(
                d.xpath('.//preceding::span[@class="field-heading"][1]/text()')
            )
            city = a.city or "<MISSING>"
            ph = d.xpath("./div[3]//text()") or "<MISSING>"
            phone = "<MISSING>"
            if ph == "<MISSING>":
                ph = d.xpath("./div[2]/p[2]/text()")
            for p in ph:
                if "T:" in p:
                    phone = str(p).replace("\n", "").strip()
                    break
            if street_address == "<MISSING>":
                street_address = ad.split(",")[0].replace(f"{city}", "").strip()
            phone = phone.replace("T:", "").strip()

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
                hours_of_operation=SgRecord.MISSING,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
