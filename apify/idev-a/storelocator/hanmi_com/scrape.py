from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _time(start, end):
    times = "closed"
    if start and end:
        times = f"{start}-{end}"
    return times


def fetch_data():
    locator_domain = "https://www.altamed.org/"
    base_url = "https://hosted.where2getit.com/hanmi/locator.html"
    page_url = "https://www.hanmi.com/about-us/locations"
    json_url = "https://hosted.where2getit.com/hanmi/rest/locatorsearch?like=0.6647255896918804"
    with SgRequests() as session:
        appkey = (
            session.get(base_url, headers=_headers)
            .text.split("appkey:")[1]
            .split("autoStart")[0]
            .strip()[1:-2]
        )
        payload = {
            "request": {
                "appkey": appkey,
                "formdata": {
                    "geoip": "start",
                    "dataview": "store_default",
                    "limit": "100",
                    "geolocs": {
                        "geoloc": [
                            {
                                "addressline": "",
                                "country": "",
                                "latitude": "",
                                "longitude": "",
                            }
                        ]
                    },
                    "searchradius": "15",
                    "where": {
                        "internalname": {"ne": "ATM"},
                        "or": {"atm": {"ilike": ""}, "branch_type": {"eq": ""}},
                    },
                },
                "geoip": "1",
            }
        }
        locations = session.post(json_url, headers=_headers, json=payload).json()
        for _ in locations["response"]["collection"]:
            street_address = _["address1"]
            if _["address2"]:
                street_address += " " + _["address2"]
            hours = []
            hours.append(f"Mon: {_time(_['mon_open'], _['mon_close'])}")
            hours.append(f"Tue: {_time(_['tues_open'], _['tues_close'])}")
            hours.append(f"Wed: {_time(_['wed_open'], _['wed_close'])}")
            hours.append(f"Thu: {_time(_['thurs_open'], _['thurs_close'])}")
            hours.append(f"Fri: {_time(_['fri_open'], _['fri_close'])}")
            hours.append(f"Sat: {_time(_['sat_open'], _['sat_close'])}")
            hours.append(f"Sun: {_time(_['sun_open'], _['sun_close'])}")
            yield SgRecord(
                page_url=page_url,
                location_name=_["internalname"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["postalcode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
