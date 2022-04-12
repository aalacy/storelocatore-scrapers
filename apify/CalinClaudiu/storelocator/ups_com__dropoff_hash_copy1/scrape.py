from bs4 import BeautifulSoup as b4

from sgscrape import sgpostal as parser

from sgscrape.pause_resume import SerializableRequest, CrawlStateSingleton
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests.sgrequests import SgRequests
import json

MISSING = "<MISSING>"  # sorry


def record_initial_requests(state):
    url = "https://www.ups.com/dropoff/res?Locations="
    numbers = "1,"
    i = 2
    while i < 250000:
        numbers = numbers + str(i) + ","
        if len(numbers) > 245:
            numbers = numbers.rsplit(",", 2)[0]
            state.push_request(SerializableRequest(url=url + numbers))
            numbers = str(i) + ","
        i += 1
    numbers = numbers[0:-1]
    state.push_request(SerializableRequest(url=url + numbers))
    return True  # signal that we've initialized the request queue.


def human_hours(x):
    hours = []
    for day in x:
        try:
            if "rue" in str(day["twentyFourHoursIndicator"]):
                hours.append(str(day["dayOfWeek"]) + ": 24h")
            else:
                hours.append(
                    str(day["dayOfWeek"])
                    + ": "
                    + str(day["openTime"])
                    + "-"
                    + str(day["closeTime"])
                )
        except Exception:
            pass
    if len(hours) == 0:
        if len(x) > 0:
            return str(x)
        return MISSING
    return "; ".join(hours)


def parsez_address(x):
    k = {}
    x = x.replace(",", " ").replace("  ", " ")
    parsed = parser.parse_address_usa(x)
    if parsed.country:
        if any(i in parsed.country for i in ["us", "US", "nited"]):
            k["country"] = parsed.country if parsed.country else MISSING
            k["address"] = (
                parsed.street_address_1 if parsed.street_address_1 else MISSING
            )
            k["address"] = (
                (k["address"] + ", " + parsed.street_address_2)
                if parsed.street_address_2
                else k["address"]
            )
            k["city"] = parsed.city if parsed.city else MISSING
            k["state"] = parsed.state if parsed.state else MISSING
            k["zip"] = parsed.postcode if parsed.postcode else MISSING
        else:
            parsed = parser.parse_address_intl(x)
            k["country"] = parsed.country if parsed.country else MISSING
            k["address"] = (
                parsed.street_address_1 if parsed.street_address_1 else MISSING
            )
            k["address"] = (
                (k["address"] + ", " + parsed.street_address_2)
                if parsed.street_address_2
                else k["address"]
            )
            k["city"] = parsed.city if parsed.city else MISSING
            k["state"] = parsed.state if parsed.state else MISSING
            k["zip"] = parsed.postcode if parsed.postcode else MISSING
    else:
        parsed = parser.parse_address_intl(x)
        k["country"] = parsed.country if parsed.country else MISSING
        k["address"] = parsed.street_address_1 if parsed.street_address_1 else MISSING
        k["address"] = (
            (k["address"] + ", " + parsed.street_address_2)
            if parsed.street_address_2
            else k["address"]
        )
        k["city"] = parsed.city if parsed.city else MISSING
        k["state"] = parsed.state if parsed.state else MISSING
        k["zip"] = parsed.postcode if parsed.postcode else MISSING
    return k


def fetch_records(http, state):
    for next_r in state.request_stack_iter():
        data = http.get(next_r.url)
        soup = b4(data.text, "lxml")
        son = soup.find("input", {"type": True, "id": "locationJson", "value": True})[
            "value"
        ]
        try:
            son = json.loads(son)
        except Exception:
            pass
        for rec in son:
            address = parsez_address(rec["address"])
            yield SgRecord(
                page_url=MISSING,
                location_name=rec["locationName"],
                street_address=address["address"],
                city=address["city"],
                state=address["state"],
                zip_postal=address["zip"],
                country_code=address["country"],
                store_number=rec["locationId"],
                phone=rec["phoneNumber"],
                location_type=str(rec["locationTypeId"])
                + " - "
                + str(rec["locationTypeName"]),
                latitude=rec["geoLatitude"],
                longitude=rec["geoLongitude"],
                locator_domain="ups.com",
                hours_of_operation=human_hours(rec["locRegularOperatingHours"]),
                raw_address=rec["address"],
            )


if __name__ == "__main__":
    state = CrawlStateSingleton.get_instance()
    ye = state.get_misc_value(
        "init", default_factory=lambda: record_initial_requests(state)
    )
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)
    ) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http, state):
                writer.write_row(rec)
