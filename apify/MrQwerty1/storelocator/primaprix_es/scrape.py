from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[contains(@class, 'tienda eleTienda-')]")

    for d in divs:
        line = d.xpath(
            ".//h2[not(contains(text(), 'Horario'))]/following-sibling::p[1]/text()"
        )
        line = list(filter(None, [li.strip() for li in line]))
        raw_address = ", ".join(line)
        zc = line.pop().replace(",", "")
        street_address = ", ".join(line)
        postal = zc.split()[0]
        city = zc.replace(postal, "").strip()
        state = "".join(d.xpath("./@data-region"))
        if "," in state:
            state = state.split(",")[-1].strip()
        country_code = "ES"
        store_number = (
            "".join(d.xpath("./@class")).split("-")[-1].replace("active", "").strip()
        )
        location_name = "".join(
            d.xpath(".//h2[not(contains(text(), 'Horario'))]/text()")
        ).strip()
        latitude = "".join(d.xpath("./@data-lat"))
        longitude = "".join(d.xpath("./@data-lng"))
        hours = d.xpath(
            ".//h2[contains(text(), 'Horario')]/following-sibling::p/text()"
        )
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours)

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
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://primaprix.es/"
    page_url = "https://primaprix.es/tiendas/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
