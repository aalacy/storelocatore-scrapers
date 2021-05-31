from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://ebsb.com"
    base_url = "https://ebsb.com/locationsapi/st_locations/get"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["results"]["Results"]:
            page_url = (
                locator_domain + f"/EBSBLocationHandler.ashx?id={_['LocationGuid']}"
            )
            hours = []
            if _["Hours"][0]["HourSetName"] == "Lobby Hours":
                for hh in _["Hours"][0]["Hours"]:
                    day = hh["StartDay"]
                    if hh["EndDay"]:
                        day += f"-{hh['EndDay']}"
                    hours.append(f"{day}: {hh['OpenTime']}-{hh['CloseTime']}")
            elif "ATM Available 24/7" == _["Hours"][0]["HourSetName"]:
                hours = ["ATM Available 24/7"]
            location_type = ""
            if _["LocationHasAtm"]:
                location_type = "atm"
            if _["LocationManager"]:
                location_type += ",branch"
            yield SgRecord(
                page_url=page_url,
                location_name=_["LocationName"],
                street_address=_["LocationAddress"],
                city=_["LocationCity"],
                state=_["LocationState"],
                zip_postal=_["LocationZipCode"],
                latitude=_["LocationLat"],
                longitude=_["LocationLon"],
                country_code="US",
                phone=_["LocationPhone"],
                locator_domain=locator_domain,
                location_type=location_type,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
