from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.artichokepizza.com/"
    base_url = "https://www.artichokepizza.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = json.loads(
            soup.find("script", type="application/ld+json").string.strip()
        )
        for _ in locations["subOrganization"]:
            if re.search(r"coming soon", _["name"], re.IGNORECASE):
                continue
            soup1 = bs(session.get(_["url"], headers=_headers).text, "lxml")
            title = soup1.find(
                "h2", string=re.compile(r"Hours & Location", re.IGNORECASE)
            )
            if not title:
                title = soup1.find(
                    "h1", string=re.compile(r"Hours & Location", re.IGNORECASE)
                )
            hours = []
            for hh in title.find_next_siblings("p")[1:]:
                if re.search(r"now open", hh.text, re.IGNORECASE):
                    continue
                if re.search(r"order online", hh.text, re.IGNORECASE):
                    break
                hours.append("; ".join(hh.stripped_strings))

            yield SgRecord(
                page_url=_["url"],
                location_name=_["name"],
                street_address=_["address"]["streetAddress"],
                city=_["address"]["addressLocality"],
                state=_["address"]["addressRegion"],
                zip_postal=_["address"]["postalCode"],
                country_code="US",
                phone=_["telephone"],
                latitude=soup1.select_one("div.gmaps")["data-gmaps-lat"],
                longitude=soup1.select_one("div.gmaps")["data-gmaps-lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
