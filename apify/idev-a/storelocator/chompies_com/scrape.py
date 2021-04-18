from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://chompies.com"
    base_url = "https://chompies.com/online-store/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("aside#sow-editor-4 div.siteorigin-widget-tinymce a")[2:]
        for link in links:
            page_url = locator_domain + link["href"]
            _ = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = parse_address_intl(
                _.select_one("p#ctl01_rptAddresses_ctl00_pAddressInfo").text.strip()
            )
            coord = _.iframe["src"].split("!2d")[1].split("!2m")[0].split("!3d")
            yield SgRecord(
                page_url=page_url,
                location_name=_.h2.text,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=coord[0],
                longitude=coord[1],
                country_code="US",
                phone=_.select_one("p#ctl01_rptAddresses_ctl00_pPhonenum")
                .text.split(":")[-1]
                .strip(),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
