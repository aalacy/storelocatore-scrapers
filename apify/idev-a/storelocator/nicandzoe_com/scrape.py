from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _phone(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    locator_domain = "https://www.nicandzoe.com/"
    base_url = "https://www.nicandzoe.com/stores/?showMap=true"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.store-locator-featured .row .col-lg-4.col-md-4")
        for _ in locations:
            location_name = _.select_one(".store-name").text.strip()
            addr = parse_address_intl(_.select_one("address a").text.strip())
            try:
                coord = (
                    _.select_one("address a")["href"]
                    .split("/@")[1]
                    .split("z/data")[0]
                    .split(",")
                )
            except:
                coord = ["", ""]

            phone = _.select("address div")[1].text
            hours_of_operation = "; ".join(
                [hh.text for hh in _.select("address div")[2:]]
            )
            if not _phone(phone):
                phone = _.select("address div")[0].text
                hours_of_operation = "; ".join(
                    [hh.text for hh in _.select("address div")[1:]]
                )
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                latitude=coord[0],
                longitude=coord[1],
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
