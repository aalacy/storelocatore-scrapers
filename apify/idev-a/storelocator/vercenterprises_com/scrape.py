from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

_data = {"action": "get_all_stores", "lat": "", "lng": ""}


def fetch_data():
    locator_domain = "https://vercenterprises.com/"
    base_url = "https://vercenterprises.com/wp-admin/admin-ajax.php"
    with SgRequests() as session:
        locations = session.post(base_url, headers=_headers, data=_data).json()
        for key, _ in locations.items():
            hours = []
            if _["op"]:
                mon = f"Mon: {_['op']['0']}"
                if _["op"]["1"]:
                    mon += f"-{_['op']['1']}"
                hours.append(mon)
                Tue = f"Tue: {_['op']['2']}"
                if _["op"]["3"]:
                    Tue += f"-{_['op']['3']}"
                hours.append(Tue)
                Wed = f"Wed: {_['op']['4']}"
                if _["op"]["5"]:
                    Wed += f"-{_['op']['5']}"
                hours.append(Wed)
                Thu = f"Thu: {_['op']['6']}"
                if _["op"]["7"]:
                    Thu += f"-{_['op']['7']}"
                hours.append(Thu)
                Fri = f"Fri: {_['op']['8']}"
                if _["op"]["9"]:
                    Fri += f"-{_['op']['9']}"
                hours.append(Fri)
                Sat = f"Sat: {_['op']['10']}"
                if _["op"]["11"]:
                    Sat += f"-{_['op']['11']}"
                hours.append(Sat)
                Sun = f"Sun: {_['op']['12']}"
                if _["op"]["13"]:
                    Sun += f"-{_['op']['13']}"
                hours.append(Sun)
            yield SgRecord(
                page_url=_["gu"],
                location_name=_["na"].strip(),
                store_number=_["ID"],
                street_address=_["st"].strip(),
                city=_["ct"].strip(),
                state=_["rg"].strip(),
                zip_postal=_["zp"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["co"].strip(),
                phone=_["te"].strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
