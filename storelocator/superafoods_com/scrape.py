from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.superafoods.com/"
    base_url = "https://www.superafoods.com/stores/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(
            "table.dwd_map_extended_child tr.et_pb_map_pin_extended"
        )
        for _ in locations:
            td = _.select_one("td.dwd_map_pin")
            info = _.select_one("td.infowindow")
            city_state = info.select_one(".infoCsz").text.split(",")
            yield SgRecord(
                page_url=base_url,
                location_name=td["data-title"],
                street_address=info.select_one(".infoStreet").text,
                city=city_state[0],
                state=city_state[1].strip().split(" ")[0].strip(),
                latitude=td["data-lat"],
                longitude=td["data-lng"],
                zip_postal=city_state[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=info.select_one(".infoPhone").text,
                hours_of_operation=info.select_one(".infoHours").text,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
