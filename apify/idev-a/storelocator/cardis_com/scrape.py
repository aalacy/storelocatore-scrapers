from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.cardis.com/"
    base_url = "https://www.cardis.com/pages/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.Grid div.Grid__Cell")
        for _ in locations:
            if not _.text.strip():
                continue
            name = ""
            if _.h4:
                name = " ".join(_.h4.stripped_strings)
            elif _.h5:
                name = " ".join(_.h5.stripped_strings)
            addr = list(_.address.stripped_strings)
            hours = []
            for x, hh in enumerate(addr):
                if hh.strip().startswith("Monday"):
                    hours += addr[x:]
                    break

            state_zip = addr[1].split(",")[1].strip().split(" ")
            coord = _.iframe["src"].split("!2d")[1].split("!2m")[0].split("!3d")
            yield SgRecord(
                page_url=base_url,
                location_name=" ".join(name).replace("’", "'"),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=state_zip[0],
                zip_postal=state_zip[-1],
                country_code="US",
                phone=_.find("a", href=re.compile(r"tel:")).text,
                latitude=coord[1],
                longitude=coord[0],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
