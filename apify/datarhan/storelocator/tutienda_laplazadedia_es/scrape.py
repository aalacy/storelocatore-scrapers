import gzip
import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.dia.es/clubdia/ES/tiendas.v{}.json.gz"
    domain = "tutienda.laplazadedia.es"
    for i in range(1573, 2000):
        response = session.get(start_url.format(i))
        if response.status_code == 200:
            break
    all_locations = json.loads(gzip.decompress(response.content))

    for poi in all_locations:
        store_number = poi["idTienda"]
        poi_url = f"https://tutienda.dia.es/buscadorTiendas.html?action=buscarInformacionTienda&id={store_number}"
        data = session.get(poi_url).json()
        hoo = []
        days_dict = {
            "1": "Lunes",
            "2": "Martes",
            "3": "Miércoles",
            "4": "Jueves",
            "5": "Viernes",
            "6": "Sábado",
            "7": "Domingo",
        }
        for i, hours in data["horariosTienda"].items():
            hoo.append(f"{days_dict[i]}: {hours}")
        hoo = ", ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url="https://tutienda.laplazadedia.es/",
            location_name=data["direccionPostal"],
            street_address=data["direccionPostal"],
            city=data["localidad"],
            state="",
            zip_postal=data["codigoPostal"],
            country_code="ES",
            store_number=store_number,
            phone=data["telefono"],
            location_type=data["tipoTienda"],
            latitude=poi["posicionX"],
            longitude=poi["posicionY"],
            hours_of_operation=hoo,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
