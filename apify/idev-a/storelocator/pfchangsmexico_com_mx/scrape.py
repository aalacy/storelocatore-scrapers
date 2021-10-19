from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://pfchangsmexico.com.mx"
base_url = "https://pfchangsmexico.com.mx/ubicaciones/"


def fetch_data():
    with SgRequests(verify_ssl=False) as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        panels = soup.select("div.vc_tta-panels div.vc_tta-panel")
        for panel in panels:
            locations = panel.select("div.vc_tta-panel-body > div")
            for _ in locations:
                if not _.p:
                    continue
                p1 = list(_.p.stripped_strings)
                raw_address = " ".join(p1[1:])
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                phone = ""
                if _.select("p")[1].a:
                    phone = _.select("p")[1].a.text.strip()
                hours = []
                if _.table:
                    hours = [
                        ": ".join(hh.stripped_strings)
                        for hh in _.select("table.wpsl-opening-hours tr")
                    ]
                yield SgRecord(
                    page_url=base_url,
                    location_name=p1[0],
                    street_address=street_address,
                    city=panel["id"],
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="Mexico",
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
