from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("acepuertorico")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.acepuertorico.com"
base_url = "https://www.acepuertorico.com/localidades/"
days = ["Lunes a Viernes", "Sábado", "Domingo"]


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.l-main h6 a")
        for link in locations:
            hours = []
            addr = []
            phone = ""
            if link["href"].startswith("http"):
                page_url = link["href"]
                logger.info(page_url)
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                addr = [
                    dd.text.strip()
                    for dd in sp1.select(
                        "div.style_blueberry_footer div.float-md-right div div"
                    )[1:-1]
                ]
                phone = list(
                    sp1.select("div.style_blueberry_footer div.float-md-right div div")[
                        -1
                    ].stripped_strings
                )[-1]
            else:
                page_url = locator_domain + link["href"]
                logger.info(page_url)
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                block = list(
                    sp1.select_one("div.l-main div.wpb_wrapper").stripped_strings
                )[1:]
                addr = []
                phone = ""
                for x, bb in enumerate(block):
                    if "Teléfono" in bb:
                        addr = block[:x]
                        phone = block[x + 1]
                        break
                for hh in sp1.select("div.l-main div.wpb_wrapper p"):
                    if "HORARIO" in hh.text:
                        temp = list(hh.stripped_strings)[1:]
                        times = day = ""
                        for x, tt in enumerate(temp):
                            if tt.replace(":", "") in days:
                                if times:
                                    hours.append(f"{day} {times}")
                                    times = ""
                                day = tt
                            else:
                                times += tt

                            if x == len(temp) - 1:
                                hours.append(f"{day} {times}")
                        break

            yield SgRecord(
                page_url=page_url,
                location_name=link.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="Puerto Rico",
                phone=phone.split("/")[0],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
