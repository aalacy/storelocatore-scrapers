from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import SgLogSetup
import re
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("arshealth")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://arshealth.com/"
    base_url = "https://arshealth.com/ars-mid-atlantic-locations/"
    with SgRequests() as session:
        links = [
            ll
            for ll in bs(session.get(base_url, headers=_headers).text, "lxml").select(
                ".vc_row.wpb_row.section.vc_row-fluid .wpb_column.vc_column_container"
            )[2:-1]
            if ll.h4
        ]
        for _ in links:
            page_url = _.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []
            _hr = sp1.find("h5", string=re.compile(r"Office Hours"))
            if _hr:
                hours = [
                    hh
                    for hh in _hr.find_next_sibling("p").stripped_strings
                    if "Admissions" not in hh
                ]
            addr = list(
                sp1.select_one("a.tel")
                .find_parent("p")
                .find_previous_sibling("h5")
                .stripped_strings
            )
            phone = ""
            if sp1.select_one("a.tel"):
                phone = sp1.select_one("a.tel").text.strip()
            coord = (
                sp1.select_one("div.wpb_map_wraper iframe")["src"]
                .split("!2d")[1]
                .split("!3m")[0]
                .split("!2m")[0]
                .split("!3d")
            )
            yield SgRecord(
                page_url=page_url,
                location_name=" ".join(_.h4.stripped_strings),
                street_address=addr[0],
                city=addr[-1].split(",")[0].strip(),
                state=" ".join(addr[-1].split(",")[1].strip().split(" ")[:-1]),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                latitude=coord[1],
                longitude=coord[0],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
