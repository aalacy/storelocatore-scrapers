from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

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
            slugs = session.get(
                f"https://dunkin.cl/wp-admin/admin-ajax.php?action=busca_comunas&region_id={region['value']}",
                headers=_headers,
            ).json()["comuna"]
            for slug in slugs:
                page_url = f"https://dunkin.cl/locales/?region={region['value']}&comuna={slug['term_id']}#"
                logger.info(page_url)
                locations = bs(
                    session.get(page_url, headers=_headers).text, "lxml"
                ).select("div.container-mapa div.direccion")
                for _ in locations:
                    addr = parse_address_intl(_.p.b.text.strip())
                    street_address = addr.street_address_1
                    if addr.street_address_2:
                        street_address += " " + addr.street_address_2
                    hours = _.select("p")[1].b.text.strip()
                    if "Centro Comercial" in hours:
                        hours = ""
                    yield SgRecord(
                        page_url=page_url,
                        location_name=_.h3.text.strip(),
                        street_address=street_address,
                        city=addr.city,
                        state=addr.state,
                        zip_postal=addr.postcode,
                        country_code="Chile",
                        locator_domain=locator_domain,
                        hours_of_operation=hours.split("/")[0]
                        .replace("–", "-")
                        .strip(),
                    )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
