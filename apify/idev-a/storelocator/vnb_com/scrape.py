from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("vnb")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.vnb.com/"
    base_url = (
        "https://www.vnb.com/index.php/contact/locations/office-locations-directions"
    )
    atm_url = "https://www.vnb.com/index.php/contact/atm-locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        _bank = soup.find("", string=re.compile(r"Bank Locations"))
        sibs = list(_bank.find_parent().find_next_siblings())
        logger.info(f"{len(sibs)/3} found")
        for x in range(0, len(sibs), 3):
            addr = list(sibs[x + 1].stripped_strings)
            temp = "".join(addr[-1].split(":")[1:]).split(",")
            hours = []
            for hh in temp:
                if "appointment" in hh.lower():
                    continue
                hours.append(hh)
            try:
                coord = (
                    sibs[x + 2].a["href"].split("/@")[1].split("/data")[0].split(",")
                )
            except:
                try:
                    coord = (
                        sibs[x + 2]
                        .a["href"]
                        .split("!3d")[1]
                        .split("!3m")[0]
                        .split("!4d")
                    )
                except:
                    try:
                        coord = (
                            sibs[x + 2]
                            .a["href"]
                            .split("ll=")[1]
                            .split("&")[0]
                            .split(",")
                        )
                    except:
                        coord = ["", ""]

            yield SgRecord(
                page_url=base_url,
                location_name=sibs[x].text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=addr[2],
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                location_type="bank",
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )

        sp1 = bs(session.get(atm_url, headers=_headers).text, "lxml")
        sibs = sp1.select("div#content div.section p")
        logger.info(f"{len(sibs[:-1])} found")
        for _ in sibs[:-1]:
            addr = list(_.stripped_strings)
            if "Back to top" in addr[0] or "please visit" in addr[0]:
                continue
            try:
                yield SgRecord(
                    page_url=atm_url,
                    location_name=addr[0],
                    street_address=addr[1],
                    city=addr[2].split(",")[0].strip(),
                    state=addr[2]
                    .replace("\xa0", " ")
                    .split(",")[1]
                    .strip()
                    .split(" ")[0]
                    .strip(),
                    zip_postal=addr[2]
                    .replace("\xa0", " ")
                    .split(",")[1]
                    .strip()
                    .split(" ")[-1]
                    .strip(),
                    country_code="US",
                    locator_domain=locator_domain,
                    location_type="atm",
                )
            except:
                import pdb

                pdb.set_trace()


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
