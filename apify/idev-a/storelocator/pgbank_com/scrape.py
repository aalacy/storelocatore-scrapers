from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.pgbank.com/"
    base_url = "https://pgbank.locatorsearch.com/GetItems.aspx"
    with SgRequests() as session:
        data = {
            "lat": "40.67377518049605",
            "lng": "-74.631655",
            "searchby": "FCS|FIATM|ATMSF|PWM|PB|",
            "SearchKey": "",
            "rnd": "1623047742075",
        }
        locations = bs(
            session.post(base_url, headers=_headers, data=data)
            .text.replace("<![CDATA[", "")
            .replace("]]>", ""),
            "lxml",
        ).select("marker")
        for _ in locations:
            hours = []
            if _.table:
                hours = ["".join(hh.stripped_strings) for hh in _.table.select("tr")]
            phone = ""
            if _.b:
                phone = _.b.text
            zip_postal = _.add2.text.split(",")[1].strip().split(" ")[-1].strip()
            if phone:
                zip_postal = zip_postal.replace(phone, "")
            yield SgRecord(
                page_url="",
                location_name=_.title.text,
                street_address=_.add1.text,
                city=_.add2.text.split(",")[0].strip(),
                state=_.add2.text.split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=zip_postal,
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=phone,
                location_type=_["icon"].split("/")[-1].split("_")[0],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
