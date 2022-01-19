from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _time(start, end):
    times = "closed"
    if start and end:
        times = f"{start}-{end}"
    return times


def fetch_data():
    locator_domain = "https://www.hanmi.com/"
    json_url = "https://hosted.where2getit.com/hanmi/rest/locatorsearch"
    page_url = "https://hosted.where2getit.com/hanmi/index.html"
    with SgRequests() as session:
        appkey = (
            session.get(page_url, headers=_headers)
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
                    "limit": "5000",
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
                    "searchradius": "5000",
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
            res = session.get(page_url, headers=_headers)
            if res.status_code != 200:
                continue

            location_type = ""
            if _["branch_type"] == "1":
                location_type = "branch"
            elif _["branch_type"] == "2":
                location_type = "Loan Center"
            elif _["branch_type"] == "3":
                location_type = "Corporate Banking Center"
            elif _["atm_type"]:
                location_type = "atm"
            else:
                location_type = _["branch_type"]
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
            page_url = f"https://locations.hanmi.com/{_['state'].lower()}/{'-'.join(_['city'].lower().strip().split(' '))}/{_['clientkey']}/"

            if _["temp_closed"]:
                hours = ["temporarily closed"]
            yield SgRecord(
                page_url=page_url,
                store_number=_["clientkey"],
                location_name=_["internalname"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["postalcode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country"],
                location_type=location_type,
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STORE_NUMBER})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
