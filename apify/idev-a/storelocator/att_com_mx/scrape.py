from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("att")

_headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/json; charset=utf-8",
    "Host": "www.att.com.mx",
    "node-path": "/content/ATT/att-personal/home/localiza-tu-tienda/jcr:content/root/responsivegrid/buscador_tiendas_cop",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
    "request-type": "states",
}

header1 = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/json; charset=utf-8",
    "Host": "www.att.com.mx",
    "request-type": "counties",
    "node-path": "/content/ATT/att-personal/home/localiza-tu-tienda/jcr:content/root/responsivegrid/buscador_tiendas_cop",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.att.com.mx"
base_url = "https://www.att.com.mx/localiza-tu-tienda"
json_url = "https://www.att.com.mx/bin/att/storefinder"


def _v(val):
    _city = val.replace("&amp;", "&")
    return (
        _city.replace("&iacute;", "í")
        .replace("&oacute;", "ó")
        .replace("&Aacute;", "Á")
        .replace("&uacute;", "ú")
        .replace("&ntilde;", "ñ")
        .replace("&aacute;", "á")
        .replace("&eacute;", "é")
    )


def fetch_data():
    with SgRequests() as session:
        session.get(base_url, headers=_headers)
        states = session.get(json_url, headers=_headers).json()["data"]
        logger.info(f"{len(states)} states")
        for state in states:
            header1["state"] = state["id"]
            header1["request-type"] = "counties"
            cities = session.get(json_url, headers=header1).json()["data"]
            logger.info(f"[{state['value']}] {len(cities)} cities")
            for city in cities:
                _city = _v(city["value"])
                header1["county"] = _city.encode("utf-8")
                header1["request-type"] = "plans"
                try:
                    res = session.get(json_url, headers=header1)
                    if res.status_code != 200:
                        continue
                    locations = res.json()["objectResponse"]
                except:
                    continue
                logger.info(f"[{state['value']}] [{_city}] {len(locations)} locations")
                for _ in locations:
                    title = list(bs(_["tienda"], "lxml").stripped_strings)
                    addr = list(bs(_["direccion"], "lxml").stripped_strings)
                    yield SgRecord(
                        page_url=base_url,
                        location_name=title[0],
                        street_address=addr[0],
                        city=_city,
                        state=_v(state["value"]),
                        zip_postal="CP. " + addr[1].split("CP.")[-1],
                        country_code="Mexico",
                        locator_domain=locator_domain,
                        hours_of_operation=title[1].replace(",", ";"),
                        raw_address=" ".join(addr),
                    )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
