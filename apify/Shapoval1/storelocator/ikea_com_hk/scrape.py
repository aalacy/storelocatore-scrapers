from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.ikea.com.hk/en/"
    api_url = "https://www.ikea.com.hk/en/where-are-we/store"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[contains(text(), " Store")]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        location_name = "".join(d.xpath(".//text()"))
        country_code = "".join(d.xpath(".//preceding::h4[1]/text()"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ad = (
            "".join(
                tree.xpath('//strong[text()="Address:"]/following-sibling::text()[1]')
            )
            .replace("\n", "")
            .strip()
        )
        if country_code == "Hong Kong":
            ad = (
                "".join(
                    tree.xpath(
                        '//strong[text()="Address:"]/following-sibling::text()[2]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        city = a.city or "<MISSING>"
        if country_code == "Hong Kong":
            city = location_name.replace("Store", "").strip()
        map_link = "".join(tree.xpath("//iframe/@src")) or "<MISSING>"
        try:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        contacts = tree.xpath(
            '//strong[contains(text(), "Contact Details:")]/following-sibling::text()'
        )
        phone = "".join(contacts[2]).split(":")[1].strip()
        hours_of_operation = (
            "".join(tree.xpath('//strong[text()="Store"]/following-sibling::text()[1]'))
            .replace("\n", "")
            .strip()
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
