from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _dd(blocks, street):
    name = phone = ""
    for bb in blocks:
        if bb.select_one("div.mk-text-block p").text.startswith(street.split(" ")[0]):
            name = bb.h2.text.strip()
            phone = bb.select("p")[-1].text.strip()
            break
    return name, phone


def fetch_data():
    locator_domain = "http://fruiterie440.com/"
    base_url = "http://fruiterie440.com/"
    with SgRequests() as session:
        sp1 = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = json.loads(
            sp1.select_one("div.mk-advanced-gmaps")[
                "data-advancedgmaps-config"
            ].replace("&quot;", '"')
        )["places"]
        blocks = sp1.select("div#succursales  div.vc_col-sm-6.vc_column_container")
        hours = [":".join(hh.stripped_strings) for hh in sp1.select("table.heures tr")]
        for _ in locations:
            addr = _["address"].split(",")
            name, phone = _dd(blocks, addr[0])
            yield SgRecord(
                page_url=base_url,
                location_name=name,
                street_address=addr[0],
                city=addr[1],
                state=addr[2].strip().split(" ")[0].strip(),
                zip_postal=" ".join(addr[2].strip().split(" ")[1:]),
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="CA",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("à", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
