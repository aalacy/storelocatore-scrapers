import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.holidayseniorliving.com/"
    api_url = "https://www.holidayseniorliving.com/search-for-senior-apartments"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//li[@class="footer-top__item text"]/a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        spage_url = f"https://www.holidayseniorliving.com{slug}"

        session = SgRequests()
        r = session.get(spage_url, headers=headers)
        tree = html.fromstring(r.text)
        jsblock = (
            "".join(tree.xpath('//script[contains(text(), "var communities")]/text()'))
            .split("var communities = ")[1]
            .split(";")[0]
            .strip()
        )
        js = json.loads(jsblock)
        for j in js:
            slug = j.get("Url")
            page_url = f"https://www.holidayseniorliving.com{slug}"
            location_name = j.get("Name") or "<MISSING>"
            street_address = j.get("Address") or "<MISSING>"
            state = j.get("State") or "<MISSING>"
            postal = j.get("ZipCode") or "<MISSING>"
            country_code = "US"
            city = j.get("City") or "<MISSING>"
            latitude = j.get("Latitude") or "<MISSING>"
            longitude = j.get("Longitude") or "<MISSING>"
            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            ph = tree.xpath('//a[contains(@href, "tel")]/text()')
            phone = "".join(ph[1]).replace("Call", "").strip() or "<MISSING>"

            hours = (
                " ".join(
                    tree.xpath(
                        '//div[.//h2[contains(text(), "Senior Apartments")]]/following-sibling::div[1]/p/span/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = "<MISSING>"
            if hours.find("We're here from") != -1:
                hours_of_operation = (
                    hours.split("We're here from")[1].split("and ")[0].strip()
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
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
