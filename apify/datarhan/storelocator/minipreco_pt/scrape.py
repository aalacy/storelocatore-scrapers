from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data():
    session = SgRequests()

    start_url = "https://lojas.minipreco.pt/buscadorTiendas.html?action=buscarTiendaCoordenadasInicio&posicionXMin={}&posicionXMax={}&posicionYMin={}&posicionYMax={}&centerX={}&centerY={}&cluster=true&tipoOrigen="
    domain = "minipreco.pt"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Requested-With": "XMLHttpRequest",
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.PORTUGAL], expected_search_radius_miles=5
    )
    for lat, lng in all_coords:
        all_locations = session.get(
            start_url.format(
                lat - 0.25, lat + 0.25, lng + 0.055, lng - 0.055, lat, lng
            ),
            headers=hdr,
        )
        if all_locations.status_code != 200:
            continue
        all_locations = all_locations.json()
        for poi in all_locations:
            store_number = poi["codigo"]
            url = "https://lojas.minipreco.pt/buscadorTiendas.html?action=buscarInformacionTienda&codigo={}"
            data = session.get(url.format(store_number)).json()[0]
            hoo = []
            days = {
                "1": "Segunda-feira",
                "2": "Terça-feira",
                "3": "Quarta-feira",
                "4": "Quinta-feira",
                "5": "Sexta-feira",
                "6": "Sábado",
                "7": "Domingo",
            }
            for i, hours in data["horariosTienda"].items():
                hoo.append(f"{days[i]}: {hours}")
            hoo = ", ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url="https://lojas.minipreco.pt/buscador-tiendas/",
                location_name="",
                street_address=data["direccionPostal"],
                city=data["localidad"],
                state="",
                zip_postal=data["codigoPostal"],
                country_code="PT",
                store_number=store_number,
                phone=data["telefono"],
                location_type=poi["negocio"],
                latitude=poi["x"],
                longitude=poi["y"],
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
