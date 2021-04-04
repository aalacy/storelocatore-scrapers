from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _phone(val):
    return (
        val.replace(")", "")
        .replace("(", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    locator_domain = "https://thecoop.ca/"
    base_url = "https://thecoop.ca/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(
            "div.vc_row.vc_row-fluid.visible-phone.wpex-vc_row-has-fill.wpex-vc-has-custom-column-spacing"
        )
        for _ in locations:
            block = _.select("div.wpb_column.vc_column_container.vc_col-sm-6")
            addr = list(block[0].select("p")[0].stripped_strings)
            hours = list(block[0].select("p")[1].stripped_strings)[1:]
            coord = ("", "")
            try:
                coord = (
                    block[1].iframe["src"].split("!2d")[1].split("!2m")[0].split("!3d")
                )
            except:
                pass
            yield SgRecord(
                page_url=base_url,
                location_name=block[0].h2.text,
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0],
                zip_postal=" ".join(addr[1].split(",")[1].strip().split(" ")[1:]),
                country_code="CA",
                phone=addr[2],
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
