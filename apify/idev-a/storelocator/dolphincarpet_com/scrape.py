from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("dolphincarpet")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.dolphincarpet.com"
    base_url = "https://www.dolphincarpet.com/wp-content/uploads/bb-plugin/cache/912070-layout.js"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).text.split("marker_point")
        logger.info(f"{len(locations)} found")
        for loc in locations[1:-1]:
            if "info_window_text.push(" not in loc:
                continue
            _ = bs(
                loc.split("info_window_text.push(")[1]
                .strip()[:-1]
                .encode("utf8")
                .decode()
                .replace("\\", ""),
                "lxml",
            )
            hours = [
                "".join(hh.stripped_strings)
                for hh in _.select("ul.store-opening-hrs li")
            ]
            latitude = loc.split("pos['lat']")[1].split('"')[1].split('"')[0]
            longitude = loc.split("pos['lng']")[1].split('"')[1].split('"')[0]
            phone = _.select_one("div.phone").text.strip()
            addr = list(_.select_one("div.address").stripped_strings)
            url = [
                ll.strip()
                for ll in _.h4.text.lower()
                .replace("-", "")
                .replace(".", "")
                .replace(",", "")
                .split(" ")
                if ll.strip()
            ]
            page_url = f"{locator_domain}/{'-'.join(url)}"
            yield SgRecord(
                page_url=page_url,
                location_name=_.h4.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
