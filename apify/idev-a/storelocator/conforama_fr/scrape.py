from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests.sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.conforama.fr"
base_url = "https://www.conforama.fr/liste-des-magasins"


def fetch_records():
    with SgRequests(proxy_country="us") as http:
        links = bs(http.get(base_url, headers=_headers).text, "lxml").select(
            "div.list-category a"
        )
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(http.get(page_url, headers=_headers).text, "lxml")
            hours = []
            for hh in sp1.select("div.magInfo-mag-horaire ul li"):
                if not hh.text.strip():
                    continue
                if "Ouvert" in hh.text:
                    break

                ss = list(hh.stripped_strings)
                hours.append(f"{ss[0]}: {' '.join(ss[1:])}")

            if sp1.summary and "fermé définitivement" in sp1.summary.text:
                continue

            phone = ""
            if sp1.select_one("div#telSurTaxeOrder"):
                phone = sp1.select_one("div#telSurTaxeOrder").text.strip()

            addr = list(sp1.select_one("div.adress p").stripped_strings)
            street_address = addr[0]
            if street_address.endswith("-"):
                street_address = street_address[:-1]
            lat = page_url.split("lat=")[1].split("&")[0]
            long = page_url.split("long=")[1].split("&")[0]
            yield SgRecord(
                page_url=page_url,
                location_name=link.text.strip(),
                street_address=street_address,
                city=" ".join(addr[-1].strip().split()[1:]),
                zip_postal=addr[-1].strip().split()[0],
                country_code="FR",
                latitude=lat,
                longitude=long,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("\r", "").replace("\n", ""),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_records():
            writer.write_row(rec)
