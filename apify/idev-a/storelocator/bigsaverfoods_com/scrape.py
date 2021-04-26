from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import dirtyjson

logger = SgLogSetup().get_logger("bigsaverfoods")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _coord(res, _id):
    return dirtyjson.loads(
        res.split(f"marketLoc[{_id}] =")[1].split("//")[0].strip()[:-1]
    )


def _addr(res, _id):
    return (
        res.split(f"marketLoc[{_id}] =")[1]
        .split("marketLoc")[0]
        .split("marketInfo")[0]
        .split("//")[1]
        .strip()
        .split(",")
    )


def fetch_data():
    locator_domain = "https://bigsaverfoods.com/"
    base_url = "https://bigsaverfoods.com/pages/location"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        soup = bs(res, "lxml")
        locations = soup.select(".each-store-info-box")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            if _.h2.text.strip() == "Corporate Office":
                continue
            _id = _.select_one("a.click-address")["data-index"]
            coord = _coord(res, _id)
            addr = [aa.strip() for aa in _addr(res, _id)]
            _hr = _.select("p")[-1].text.strip()
            hours_of_operation = ""
            if "Store Hours" in _hr:
                hours_of_operation = _hr.replace("Store Hours:", "").strip()
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text.strip(),
                street_address=addr[0],
                city=addr[1],
                state=addr[2].split(" ")[0],
                zip_postal=addr[2].split(" ")[-1],
                country_code="US",
                phone=_.select("p")[1].text.strip().split(":")[-1],
                locator_domain=locator_domain,
                latitude=coord["lat"],
                longitude=coord["lng"],
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
