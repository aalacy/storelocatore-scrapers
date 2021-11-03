from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.novacare.com"
base_url = "https://www.novacare.com//sxa/search/results/?s={D779ED53-C5AD-46DB-AA4F-A2F78783D3B1}|{CC39E325-A49A-4785-B763-C515E5679B4D}&itemid={891FD4CE-DCBE-4AA5-8A9C-539DF5FCDE97}&sig=&autoFireSearch=true&v=%7B80D13F78-0C6F-42A0-A462-291DD2D8FA17%7D&p=10"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["Results"]
        for _ in locations:
            loc = bs(_["Html"], "lxml")
            addr = list(
                loc.select_one("div.loc-result-card-address-container").stripped_strings
            )
            hours = [
                " ".join(tr.stripped_strings)
                for tr in loc.select("div.field-businesshours table tr")
            ]
            yield SgRecord(
                page_url="",
                location_name=loc.select_one("div.loc-result-card-name").text.strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=loc.select_one(
                    "div.loc-result-card-phone-container"
                ).text.strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
