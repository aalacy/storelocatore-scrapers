from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://teste.condor.com.br/news/wp-json/wp/v2/loja?per_page=100"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        source = j.get("content1") or "<html>"
        tree = html.fromstring(source)
        street_address = "".join(
            tree.xpath(
                "//strong[contains(text(), 'Endereço')]/following-sibling::text()[1]|"
                "//b[./strong[contains(text(), 'Endereço')]]/following-sibling::text()[1]"
            )
        ).strip()
        if not street_address:
            street_address = (
                "".join(tree.xpath("//p[contains(text(), 'Endereço')]/text()"))
                .replace("Endereço", "")
                .strip()
            )
        street_address = street_address.replace(":", "")
        city = j.get("cidade")
        state = j.get("region")
        postal = j.get("ZipCode")
        country_code = "BR"
        store_number = j.get("cod_loja")
        location_name = j.get("title1")
        slug = j.get("slug")
        page_url = f"https://www.condor.com.br/lojas/{slug}"
        phone = j.get("telefone")
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = ";".join(
            tree.xpath(
                "//p[.//*[contains(text(), 'Horário')]]/following-sibling::p/text()"
            )
        ).strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.condor.com.br/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
