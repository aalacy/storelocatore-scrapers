from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("eatfitgo")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    if val:
        return val.replace("\xa0", " ").strip()
    else:
        return ""


def fetch_data():
    locator_domain = "https://www.eatfitgo.com/"
    base_url = "https://www.eatfitgo.com/pages/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.grid--flush-bottom div.grid__item")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            location_name = _.select_one(".h3").text.strip()
            logger.info(location_name)
            addr = []
            hours = []
            ps = _.select("div.rte-setting p")
            for x, aa in enumerate(ps):
                if not _valid(aa.text):
                    addr = [_valid(bb.text) for bb in ps[:x]]
                    hours = [_valid(hh.text) for hh in ps[x + 1 :] if _valid(hh.text)]
                    break

            try:
                coord = (
                    _.select("a")[-1]["href"]
                    .split("/@")[1]
                    .split("z/data")[0]
                    .split(",")
                )
            except:
                coord = ["", ""]

            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=addr[-1],
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
