from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://tacobell.es/"
    api_url = "https://tacobell.es/restaurantes/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="comunidad"]/a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))

        spage_url = f"https://tacobell.es{slug}"
        session = SgRequests()
        r = session.get(spage_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//a[contains(text(), "INFO")]')
        for d in div:

            page_url = "".join(d.xpath(".//@href"))
            location_name = (
                "".join(d.xpath(".//preceding::h2[1]/text()")).replace("\n", "").strip()
            )
            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            ad = (
                " ".join(tree.xpath('//div[@class="dir"]/text()'))
                .replace("\n", "")
                .strip()
            )
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "ES"
            city = a.city or "<MISSING>"
            latitude = (
                "".join(tree.xpath('//script[contains(text(), "var uluru")]/text()'))
                .split("lat:")[1]
                .split(",")[0]
                .strip()
                or "<MISSING>"
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "var uluru")]/text()'))
                .split("lng:")[1]
                .split("}")[0]
                .strip()
                or "<MISSING>"
            )
            phone = "".join(tree.xpath('//div[@class="tfno"]//a/text()')) or "<MISSING>"
            hours_of_operation = (
                " ".join(tree.xpath('//table[@class="c-hours-details"]//tr/td/text()'))
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
