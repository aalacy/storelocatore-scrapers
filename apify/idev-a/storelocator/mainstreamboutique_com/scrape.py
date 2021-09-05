from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import dirtyjson
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("mainstreamboutique")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    locator_domain = "https://mainstreamboutique.com"
    base_url = "https://mainstreamboutique.com/apps/store-locator"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        coords = (
            res.split("= 'You Are Here';")[1]
            .strip()
            .split("function initialize()")[0]
            .split("markersCoords.push(")
        )
        locs = []
        for temp in coords:
            if not temp:
                continue
            _ = dirtyjson.loads(temp[:-2])
            locs.append(_)

        soup = bs(res, "lxml")
        locations = soup.select("div#addresses_list ul li")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            store_number = _["onmouseover"].split("(")[1][:-1]
            city = _.select_one("span.city").text.strip()
            page_url = (
                "https://mainstreamboutique.com/pages/"
                + _.select_one("div.store_website a")["href"].split("/")[-1]
            )
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _addr = [
                aa
                for aa in sp1.select("div.shg-row > div")[0].stripped_strings
                if aa.strip()
            ][2].split()
            _addr = [aa for aa in _addr if aa.strip()]
            hours = []
            if "We are closed" in sp1.select("div.shg-row > div")[1].text:
                hours = ["Closed"]
            else:
                hh = list(sp1.select("div.shg-row > div")[1].stripped_strings)[1:]
                for x in range(0, len(hh), 2):
                    hours.append(f"{hh[x]} {hh[x+1]}")
            phone = (
                sp1.select("div.shg-row > div")[2].p.text.strip().split(":")[-1].strip()
            )

            if not _p(phone):
                phone = ""
            zip_postal = ""
            if _.select_one("span.postal_zip"):
                zip_postal = _.select_one("span.postal_zip").text.strip()
            if not zip_postal:
                zip_postal = _addr[-1].strip()
                if not zip_postal.isdigit():
                    zip_postal = ""
            coord = ["", ""]
            for loc in locs:
                if str(loc["id"]) == store_number:
                    coord = loc
                    break
            yield SgRecord(
                page_url=page_url,
                location_name=_.select_one("span.name").text.strip(),
                street_address=_.select_one("span.address").text.strip(),
                city=city,
                state=_.select_one("span.prov_state").text.strip(),
                latitude=coord["lat"],
                longitude=coord["lng"],
                zip_postal=zip_postal,
                country_code=_.select_one("span.country").text,
                locator_domain=locator_domain,
                phone=phone,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
