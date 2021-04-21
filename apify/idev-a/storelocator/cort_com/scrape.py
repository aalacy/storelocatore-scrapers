from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("mycarecompass")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.cort.com/"
    base_url = "https://www.cort.com/public/v1/storelocator?_t=1618597613068"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for key, states in locations.items():
            for _ in states:
                if "cortDisplayName" not in _:
                    continue
                try:
                    page_url = f"https://www.cort.com/locations/store/{_['cortDisplayName']}/{_['id']}"
                    logger.info(page_url)
                    url = f"https://www.cort.com/public/v1/storelocator/{_['id']}?_t=1618598972009"
                    sp1 = session.get(url, headers=_headers).json()
                    location_name = f"{_['city']}, {_['state']}"
                    street_address = _["addressLine1"]
                    if _["addressLine2"]:
                        street_address += ", " + _["addressLine2"]
                    hours = []
                    hh = sp1["storeHours"]
                    if hh["mondayOpen"] and hh["mondayClose"]:
                        time = f"{hh['mondayOpen']}-{hh['mondayClose']}"
                        if hh["mondayOpen"] == "Closed":
                            time = "Closed"
                        hours.append(f"Monday: {time}")
                    if hh["tuesdayOpen"] and hh["tuesdayClose"]:
                        time = f"{hh['tuesdayOpen']}-{hh['tuesdayClose']}"
                        if hh["mondayOpen"] == "Closed":
                            time = "Closed"
                        hours.append(f"Tuesday: {time}")
                    if hh["wednesdayOpen"] and hh["wednesdayClose"]:
                        time = f"{hh['wednesdayOpen']}-{hh['wednesdayClose']}"
                        if hh["wednesdayOpen"] == "Closed":
                            time = "Closed"
                        hours.append(f"Wednesday: {time}")
                    if hh["thursdayOpen"] and hh["thursdayClose"]:
                        time = f"{hh['thursdayOpen']}-{hh['thursdayClose']}"
                        if hh["thursdayOpen"] == "Closed":
                            time = "Closed"
                        hours.append(f"Thursday: {time}")
                    if hh["fridayOpen"] and hh["fridayClose"]:
                        time = f"{hh['fridayOpen']}-{hh['fridayClose']}"
                        if hh["fridayOpen"] == "Closed":
                            time = "Closed"
                        hours.append(f"Friday: {time}")
                    if hh["saturdayOpen"] and hh["saturdayClose"]:
                        time = f"{hh['saturdayOpen']}-{hh['saturdayClose']}"
                        if hh["saturdayOpen"] == "Closed":
                            time = "Closed"
                        hours.append(f"Saturday: {time}")
                    if hh["sundayOpen"] and hh["saturdayClose"]:
                        time = f"{hh['sundayOpen']}-{hh['sundayClose']}"
                        if hh["sundayOpen"] == "Closed":
                            time = "Closed"
                        hours.append(f"Sunday: {time}")
                except:
                    import pdb

                    pdb.set_trace()
                yield SgRecord(
                    page_url=page_url,
                    location_name=location_name,
                    location_type=_["type"],
                    street_address=street_address,
                    city=_["city"],
                    state=_["state"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    zip_postal=_["postalCode"],
                    country_code="US",
                    phone=_["phoneNumber"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
