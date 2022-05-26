from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.radley.co.uk/"
    api_url = "https://www.radley.co.uk/stores/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//h3[.//span[@class="cmp-accordion__title"]]')
    for d in div:
        location_type = "".join(d.xpath(".//span//text()"))
        page_urls = d.xpath("./following-sibling::div//a")
        for p in page_urls:
            slug = "".join(p.xpath(".//@href"))
            page_url = f"https://www.radley.co.uk{slug}"
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            location_name = "".join(tree.xpath("//h1//text()"))
            ad = tree.xpath(
                '//div[@class="cmp-googlemaps__information--text"]/p//text()'
            )
            ad = list(filter(None, [a.strip() for a in ad]))
            adr = " ".join(ad)
            a = parse_address(International_Parser(), adr)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "GB"
            if postal.isdigit():
                country_code = "US"
            city = a.city or "<MISSING>"
            if country_code == "GB":
                postal = "".join(ad[-1]).strip()
                city = "".join(ad[-2]).strip()
                street_address = " ".join(ad[:-2]).strip()
            latitude = "".join(tree.xpath("//script/@latitude")) or "<MISSING>"
            longitude = "".join(tree.xpath("//script/@longitude")) or "<MISSING>"
            phone = (
                "".join(
                    tree.xpath(
                        '//div[./div/h2[text()="CONTACT"]]/following-sibling::div[1]//i[@class="icon icon-phone cmp-iconlink__icon--left"]/following-sibling::span//text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = (
                " ".join(tree.xpath('//ul[@class="cmp-openinghours__week"]/li//text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = " ".join(hours_of_operation.split())

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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=adr,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
