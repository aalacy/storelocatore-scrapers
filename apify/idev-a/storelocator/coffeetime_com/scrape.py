from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("coffeetime")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.coffeetime.com"
base_url = (
    "http://www.coffeetime.com/locations.aspx?address=&city=&Countryui=CA&pageNumber={}"
)


def _p(val):
    return (
        val.replace("(", "")
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
    with SgRequests() as session:
        page = 1
        while True:
            soup = bs(session.get(base_url.format(page), headers=_headers).text, "lxml")
            links = soup.select("div.location-box")
            if not links:
                break
            page += 1
            logger.info(f"{len(links)} found")

            for link in links:
                addr = link.select_one("p.fontpro").text.strip().split(",")
                coord = link.img["src"].split("|")[1].split("&")[0].split(",")
                phone = link.select("ul.md-li li")[0].p.text.strip()
                if not _p(phone):
                    phone = ""
                street_address = link.select_one("p.fontXXL").text.strip()
                hours = ""
                if street_address.startswith("MON"):
                    hours = street_address.split(",")[0]
                    street_address = ", ".join(street_address.split(",")[1:])
                yield SgRecord(
                    page_url=base_url,
                    location_name=street_address,
                    street_address=street_address,
                    city=addr[0].strip(),
                    state=addr[1].strip(),
                    zip_postal=addr[2].strip(),
                    country_code="CA",
                    phone=phone,
                    locator_domain=locator_domain,
                    latitude=coord[0],
                    longitude=coord[1],
                    hours_of_operation=hours,
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
