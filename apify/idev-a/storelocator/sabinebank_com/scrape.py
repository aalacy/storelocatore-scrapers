from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.sabinebank.com/"
    base_url = "https://www.sabinebank.com/LocationsandATMs"
    with SgRequests() as session:
        locations = (
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select("table.acctTable")[0]
            .select("tr")[1:]
        )
        for _ in locations:
            addr = list(_.select("td")[0].stripped_strings)
            hours_of_operation = "; ".join(_.select("td")[1].stripped_strings)
            if (
                "Drive-Thru" in hours_of_operation
                or "No Public Access" in hours_of_operation
            ):
                hours_of_operation = ""
            zip_postal = addr[-2].split(",")[1].strip().split(" ")[-1].strip()
            if not zip_postal.strip().isdigit():
                zip_postal = ""
            yield SgRecord(
                page_url=base_url,
                location_name=addr[0],
                street_address=addr[-3],
                city=addr[-2].split(",")[0].strip(),
                state=addr[-2].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=zip_postal,
                country_code="US",
                phone=addr[-1].split(":")[1].replace("Phone", ""),
                locator_domain=locator_domain,
                location_type="branch",
                hours_of_operation=hours_of_operation,
            )

        locations = (
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select("table.acctTable")[-1]
            .select("tr td")[1:]
        )
        for _ in locations:
            addr = list(_.stripped_strings)
            if not addr:
                continue
            zip_postal = addr[-1].split(",")[1].strip().split(" ")[-1].strip()
            if not zip_postal.strip().isdigit():
                zip_postal = ""
            yield SgRecord(
                page_url=base_url,
                location_name=addr[0],
                street_address=addr[-2],
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=zip_postal,
                location_type="atm",
                country_code="US",
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
