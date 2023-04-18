from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("bennigans")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _p(val):
    return (
        val.split("and")[0]
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    locator_domain = "https://bennigans.com/"
    base_url = "https://bennigans.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = (
            soup.select_one("div#domestic")
            .find_next_sibling()
            .select("div.fusion-layout-column")
        )
        logger.info(f"{len(locations)} found")
        for _ in locations:
            addr = []
            for aa in _.h5.find_next_siblings():
                addr += list(aa.stripped_strings)
            del addr[-1]
            phone = ""
            if _p(addr[-1]):
                phone = addr[-1].split("and")[0]
                del addr[-1]

            try:
                coord = _.a["href"].split("!3d")[1].split("!3m")[0].split("!4d")
            except:
                try:
                    coord = _.a["href"].split("/@")[1].split("/data")[0].split(",")
                except:
                    coord = ["", ""]
            yield SgRecord(
                page_url=base_url,
                location_name=" ".join(_.h5.stripped_strings).replace("’", "'"),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                raw_address=" ".join(addr),
            )

        locations = (
            soup.select_one("div#international")
            .find_next_sibling()
            .select("div.fusion-layout-column")
        )
        logger.info(f"{len(locations)} found")
        for _ in locations:
            if "Delivery Only" in _.text:
                continue
            _addr = []
            for aa in _.h5.find_next_siblings():
                _addr += list(aa.stripped_strings)
            del _addr[-1]
            phone = ""
            if _p(_addr[-1]):
                phone = _addr[-1].split("and")[0]
                del _addr[-1]
            raw_address = ", ".join(_addr).replace("\xa0", " ")
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            state = addr.state
            try:
                coord = _.a["href"].split("!3d")[1].split("!3m")[0].split("!4d")
            except:
                try:
                    coord = _.a["href"].split("/@")[1].split("/data")[0].split(",")
                except:
                    coord = ["", ""]
            if addr.country == "Mexico":
                city = _addr[1].replace("\xa0", " ").split(",")[0].strip()
                state = (
                    _addr[1]
                    .replace("\xa0", " ")
                    .split(",")[1]
                    .strip()
                    .split(" ")[0]
                    .strip()
                )
            yield SgRecord(
                page_url=base_url,
                location_name=" ".join(_.h5.stripped_strings).replace("’", "'"),
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=addr.postcode,
                country_code=addr.country,
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
