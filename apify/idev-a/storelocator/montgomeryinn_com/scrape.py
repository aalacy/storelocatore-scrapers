from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.montgomeryinn.com/"
base_url = "https://www.montgomeryinn.com/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("section.c-two-col-thumbs")[0].select("div.col-md-6")
        for _ in locations:
            addr = list(_.p.stripped_strings)
            page_url = locator_domain + _.select("a")[-1]["href"]
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []
            for hh in list(sp1.select("section#intro p")[1].stripped_strings)[1:-1]:
                hours.append(hh.split("Reservations")[0].strip())
            coord = (
                sp1.select_one("div.gmaps")["data-gmaps-static-url-mobile"]
                .split("&center=")[1]
                .split("&")[0]
                .split("%2C")
            )
            yield SgRecord(
                page_url=page_url,
                location_name=_.h2.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=_.select("p")[-1].text.strip(),
                locator_domain=locator_domain,
                raw_address=" ".join(addr),
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace(",", ";").replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
