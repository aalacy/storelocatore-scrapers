from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://truevaluecompany.com"
base_url = "https://hosted.where2getit.com/truevalue/index_responsive.html"
json_url = "https://hosted.where2getit.com/truevalue/rest/locatorsearch?like=0.22822414982857775&lang=en_US"

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
coords = [
    (40.75368539999999, -73.9991637),
    (3.216264063853835, 23.092478837961707),
    (8.873924062928575, -67.8303725109154),
    (-25.180938219545883, -62.55693492432918),
    (26.57294931161124, 5.997752650887076),
    (58.8956478624396, 47.8336901788746),
    (62.827134824567196, 116.03681483952685),
    (31.488776327650406, 104.43525246284652),
    (-19.161622877728977, 129.57197119797826),
    (38.56848203215075, -85.29390630160187),
    (45.724319857723856, -112.27632804234958),
    (54.254731096987264, -2.022207494535218),
    (52.364631082042784, -8.17455121392394),
    (62.28025825907213, -104.37084024056514),
    (29.40527629075857, 42.05494108989879),
    (63.403394833977075, 25.883066178234056),
    (46.697782314730006, 65.60962839573575),
]


def get(_, key):
    if _.get(key):
        return _.get(key).strip()
    return ""


def fetch_data(app_key):
    for coord in coords:
        with SgRequests() as session:
            payload = {
                "request": {
                    "appkey": app_key,
                    "formdata": {
                        "geoip": "false",
                        "dataview": "store_default",
                        "limit": 10000,
                        "atleast": 1,
                        "geolocs": {
                            "geoloc": [
                                {
                                    "addressline": "",
                                    "country": "",
                                    "latitude": coord[0],
                                    "longitude": coord[1],
                                    "state": "",
                                    "province": "",
                                    "city": "",
                                    "address1": "",
                                    "postalcode": "",
                                }
                            ]
                        },
                        "searchradius": "5000",
                        "radiusuom": "",
                        "where": {},
                        "false": "0",
                    },
                }
            }
            locations = session.post(json_url, headers=_headers, json=payload).json()[
                "response"
            ]["collection"]

            logger.info(f"[{coord}] {len(locations)}")

            for _ in locations:
                street_address = get(_, "address1")
                if get(_, "address2"):
                    street_address += " " + get(_, "address2")
                hours = []
                for day in days:
                    day = day.lower()
                    open = get(_, f"{day}_open_time")
                    close = get(_, f"{day}_close_time")
                    if open:
                        hours.append(f"{day}: {open} {close}")

                location_type = ""
                if get(_, "carpetcleanerrental") == "1":
                    location_type = "rental store"
                if get(_, "hg") == "1":
                    location_type = "garden center"
                if get(_, "keycutting") == "1":
                    location_type = "Hardware store"

                yield SgRecord(
                    page_url=get(_, "tvurl")
                    or "https://www.truevaluecompany.com/store-locator",
                    store_number=get(_, "dealerid"),
                    location_name=get(_, "name"),
                    street_address=street_address,
                    city=get(_, "city"),
                    state=get(_, "state"),
                    zip_postal=get(_, "postalcode"),
                    country_code=get(_, "country"),
                    phone=get(_, "phone"),
                    latitude=get(_, "latitude"),
                    longitude=get(_, "longitude"),
                    location_type=location_type,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    app_key = None
    with SgRequests() as session:
        app_key = (
            session.get(base_url, headers=_headers)
            .text.split("<appkey>")[1]
            .split("</appkey>")[0]
        )
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.LOCATION_TYPE,
                }
            ),
            duplicate_streak_failure_factor=100,
        )
    ) as writer:
        results = fetch_data(app_key)
        for rec in results:
            writer.write_row(rec)
