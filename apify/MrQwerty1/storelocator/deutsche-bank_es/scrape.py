from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_states():
    states = dict()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    op = tree.xpath("//select[@id='prov']/option")
    for o in op:
        key = "".join(o.xpath("./@value"))
        val = "".join(o.xpath("./text()"))
        states[key] = val

    return states


def fetch_data(sgw: SgWriter):
    states = get_states()
    api = "https://www.deutsche-bank.es/dam/spain/es/biblioteca/buscador-oficinas/infocentros_min_CP.xml"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.content)
    divs = tree.xpath("//reg")

    for d in divs:
        street_address = "".join(d.xpath("./@dir"))
        city = "".join(d.xpath("./@pob"))
        key = "".join(d.xpath("./@prov"))
        state = states.get(key)
        postal = "".join(d.xpath("./@cp"))
        country_code = "ES"
        store_number = "".join(d.xpath("./@numo"))
        location_name = "".join(d.xpath("./@nomo"))
        phone = "".join(d.xpath("./@tel")).strip()
        if phone.startswith("0") and phone.endswith("0"):
            phone = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.deutsche-bank.es/"
    page_url = "https://www.deutsche-bank.es/es/herramientas/buscador-oficinas.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
