from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json

locator_domain = "https://www.alfaromeo.co.uk"


def fetch_data():
    with SgRequests() as session:
        base_url = "https://dealerlocator.fiat.com/geocall/RestServlet?jsonp=callback&mkt=3112&brand=83&func=finddealerxml&serv=sales&track=1&x=-0.12895&y=51.50304&rad=10000&drl=1&_=1613594042811"
        res = session.get(base_url)
        store_list = json.loads(res.text[9:-1])["results"]
        for store in store_list:
            page_url = store["WEBSITE"].strip()
            location_name = store["COMPNAME2"]
            zip = store["ZIPCODE"]
            city = store["TOWN"]
            street_address = store["ADDRESS"]
            phone = store["TEL_1"]
            latitude = store["XCOORD"]
            longitude = store["YCOORD"]
            hours = store["ACTIVITY"][0]
            hours_of_operation = ""
            for x in hours:
                if x == "ACTIVITY_CODE":
                    continue
                hours_of_operation += (
                    hours[x]["DATEWEEK"]
                    + ": "
                    + (
                        hours[x]["MORNING_FROM"][:2]
                        + ":"
                        + hours[x]["MORNING_FROM"][2:]
                        + "-"
                        + hours[x]["AFTERNOON_TO"][:2]
                        + ":"
                        + hours[x]["AFTERNOON_TO"][2:]
                        + " "
                        if "MORNING_FROM" in hours[x].keys()
                        else "Closed "
                    )
                )
            record = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=zip,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
            yield record


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
