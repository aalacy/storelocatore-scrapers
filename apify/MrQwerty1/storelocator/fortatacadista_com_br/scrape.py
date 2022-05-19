import json5
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var lojas =')]/text()"))
    text = text.split("var lojas =")[1].split("];")[0].strip()[:-1] + "]"
    js = json5.loads(text)

    for j in js:
        adr1 = j.get("endereco") or ""
        adr2 = j.get("numero") or ""
        street_address = f"{adr1} {adr2}".replace("</br>", "").strip()
        city = j.get("cidade")
        state = j.get("uf")
        postal = j.get("cep")
        country_code = "BR"
        location_name = j.get("nome") or ""
        store_number = location_name.strip().split()[-1]
        phone = j.get("telefone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        _tmp = []
        source = j.get("horarioFuncionamento") or "<html>"
        root = html.fromstring(source)
        hours = root.xpath("//text()")
        for h in hours:
            if not h.strip():
                continue
            _tmp.append(h.strip())
            if "Domingo" in h:
                break
        hours_of_operation = ";".join(_tmp)

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
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.fortatacadista.com.br/"
    page_url = "https://www.fortatacadista.com.br/nossas-lojas/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests(proxy_country="br")
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
