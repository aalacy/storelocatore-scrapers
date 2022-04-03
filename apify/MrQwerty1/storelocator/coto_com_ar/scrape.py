from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.coto.com.ar/mapassucursales/Sucursales/ListadoSucursales.aspx"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//table[contains(@class, 'table table-striped')]/tbody/tr")
    days = ["Lunes a Jueves", "Viernes", "Sabado", "Domingo"]

    for d in divs:
        store_number = "".join(d.xpath("./td[1]//text()")).strip()
        location_name = "".join(d.xpath("./td[2]//text()")).strip()
        page_url = f"https://www.coto.com.ar/mapassucursales/Sucursales/DetalleSucursal.aspx?idSucursal={store_number}"
        raw_address = "".join(d.xpath("./td[3]//text()")).strip()
        location_type = (
            "".join(d.xpath("./td[4]//div[contains(@class, 'btnTipo')]/@class"))
            .replace("btnTipo", "")
            .strip()
        )

        _tmp = []
        hours = d.xpath("./td")[4:-1]
        for day, h in zip(days, hours):
            inter = "".join(h.xpath(".//text()")).strip()
            _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp)
        phone = "".join(d.xpath("./td[9]//text()")).strip()
        street_address = raw_address.split("-")[0].strip()
        city = raw_address.split("-")[1].strip()

        sep = ["/", "al", " "]
        for s in sep:
            if s in phone:
                phone = phone.split(s)[0].strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            country_code="AR",
            phone=phone,
            store_number=store_number,
            location_type=location_type,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.coto.com.ar/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
