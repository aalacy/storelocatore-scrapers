from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.mastertile.net/"
    base_url = "https://www.mastertile.net/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("ul#menu-main > li")[-1].select("ul li a")
        for link in links:
            if link["href"] == "#" or "contact" in link["href"]:
                continue
            sp1 = bs(session.get(link["href"], headers=_headers).text, "lxml")
            try:
                block = list(
                    sp1.select_one("div#location-content-details").stripped_strings
                )
                coord = (
                    sp1.select_one("div#location-map iframe")["src"]
                    .split("!2d")[1]
                    .split("!2m")[0]
                    .split("!3d")
                )
                yield SgRecord(
                    page_url=link["href"],
                    location_name=link.text,
                    street_address=block[0],
                    city=block[1].split(",")[0].strip(),
                    state=block[1].split(",")[1].strip().split(" ")[0].strip(),
                    latitude=coord[1],
                    longitude=coord[0],
                    zip_postal=block[1].split(",")[1].strip().split(" ")[-1].strip(),
                    phone=block[2].replace("Phone", ""),
                    country_code="US",
                    locator_domain=locator_domain,
                )
            except:
                import pdb

                pdb.set_trace()


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
