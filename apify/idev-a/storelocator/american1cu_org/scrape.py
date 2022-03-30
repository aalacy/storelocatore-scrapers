from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re

logger = SgLogSetup().get_logger("american1cu")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.american1cu.org"
base_url = "https://www.american1cu.org/locations"


def _coord(infos, addr):
    coord = ["", ""]
    for info in infos:
        loc = bs(info.split(");")[0][1:-1], "lxml")
        _addr = list(loc.select("p")[1].stripped_strings)
        if _addr == addr:
            coord = (
                loc.select_one("input[type='button']")["onclick"]
                .split("(")[1][:-2]
                .split(",")
            )
            break
    return coord


def _hoo(_hr):
    if _hr:
        if _hr.find_parent().find_next_sibling("blockquote"):
            return _hr.find_parent().find_next_sibling("blockquote").stripped_strings
        else:
            list(_hr.find_parent().stripped_strings)[1:]
    return []


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        infos = res.split("infowindow.setContent(")[1:]
        soup = bs(res, "lxml")
        links = soup.select("div.loc_list.Cbox div.listbox")
        logger.info(f"{len(links)} branch found")
        for link in links:
            hours = []
            _hr = link.find("strong", string=re.compile(r"Lobby Hours"))
            if _hr:
                hours = _hoo(_hr)
            else:
                _hr = link.find("strong", string=re.compile(r"Branch Hours"))
                if _hr:
                    hours = _hoo(_hr)
                else:
                    _hr = link.find("strong", string=re.compile(r"^Hours"))
                    hours = _hoo(_hr)
            addr = list(link.select("p")[1].stripped_strings)
            if "temporarily closed" in addr[0].lower():
                hours = ["Temporarily Closed"]
                addr = list(link.select("p")[2].stripped_strings)
            phone = ""
            _p = link.find("strong", string=re.compile(r"Phone"))
            if _p:
                phone = list(_p.find_parent().stripped_strings)[1]

            coord = _coord(infos, addr)
            yield SgRecord(
                page_url=base_url,
                location_name=link.select_one("span.cuname").text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                location_type="branch",
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )

        links = soup.select("div.loc_list.Abox div.listbox")
        logger.info(f"{len(links)} atm found")
        for link in links:
            addr = list(
                [pp for pp in link.select("p") if pp.text.strip()][0].stripped_strings
            )
            yield SgRecord(
                page_url=base_url,
                location_name=link.select_one("span.cuname").text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                locator_domain=locator_domain,
                location_type="atm",
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_TYPE,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
