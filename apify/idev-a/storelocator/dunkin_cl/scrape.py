from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


logger = SgLogSetup().get_logger("dunkin")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://dunkin.cl"
base_url = "https://dunkin.cl/locales/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        regions = soup.select("select#region option")
        logger.info(f"{len(regions)} found")
        for region in regions:
            if not region.get("value"):
                continue
            res = session.get(
                f"{base_url}?region={region['value']}", headers=_headers
            ).text
            slugs = bs(res, "lxml").select("select#comuna option")
            for slug in slugs:
                page_url = (
                    f"{base_url}?region={region['value']}&comuna={slug['value']}#"
                )
                logger.info(page_url)
                res1 = session.get(page_url, headers=_headers)
                if res1.status_code != 200:
                    continue
                locations = bs(res1.text, "lxml").select(
                    "div.container-mapa div.direccion"
                )
                for _ in locations:
                    location_name = _.h3.text.strip()
                    raw_address = _.p.b.text.strip()
                    addr = parse_address_intl(raw_address + ", Chile")
                    street_address = addr.street_address_1
                    if addr.street_address_2:
                        street_address += " " + addr.street_address_2

                    city = addr.city or ""
                    state = addr.state
                    if (
                        not city
                        and "Mall" not in location_name
                        and "Plaza" not in location_name
                        and "Center" not in location_name
                        and "Portal" not in location_name
                        and "Aeropuerto" not in location_name
                        and "Shop" not in location_name
                        and "Espacio" not in location_name
                        and "Estado" not in location_name
                    ):
                        city = location_name
                    if (
                        city.replace("-", "").isdigit()
                        or city == "C16"
                        or city == "A"
                        or city == "Cenit"
                        or city == "Alameda 711"
                        or city == "B-2083"
                        or city == "C-21"
                        or city == "C-365"
                    ):
                        city = ""

                    if city and "Los Ríos" in city:
                        state = "Los Ríos"
                    street_address = street_address.replace("Chile", "").strip()
                    if street_address.isdigit():
                        street_address = raw_address.split(",")[0]
                    hours = _.select("p")[1].b.text.strip()
                    if "Centro Comercial" in hours:
                        hours = ""
                    yield SgRecord(
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city.replace("Jumbo", "").replace("Los Ríos", "").strip(),
                        state=state,
                        zip_postal=addr.postcode,
                        country_code="Chile",
                        locator_domain=locator_domain,
                        hours_of_operation=hours.split("/")[0]
                        .replace("–", "-")
                        .strip(),
                        raw_address=raw_address,
                    )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
