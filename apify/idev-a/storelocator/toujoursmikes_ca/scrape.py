from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgselenium import SgChrome
import time

_headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "cookie": "_gcl_au=1.1.975363602.1616712332; _ga=GA1.2.231204879.1616712333; _gid=GA1.2.1592421006.1616712333; _dc_gtm_UA-16242043-1=1; _fbp=fb.1.1616712334110.329251647; _gat_UA-16242043-1=1; XSRF-TOKEN=eyJpdiI6IlwvNFk4MW1QcTZJSkJvZ1RTM0NEZGxBPT0iLCJ2YWx1ZSI6IkNlN3lmMkJ2SEhwMkVveExLa1B4eFR1VkMwc0o0TVpVbnFaY1l0aE1vM0pmWFdERWQrdFVSdm11T3E1MXF0cVkiLCJtYWMiOiI4NjcwZGM0YzFlYWJlNGIwNzBhY2Q3YWI4ZDZhMjU3ZjQ1OGFlY2Y5ZjJmOTBmMzdiZDc4MTlmNjY3YWMzYjA0In0%3D; mikes_session=eyJpdiI6IktsOG0rcjZRd2VnME12ZXk2R3l6VVE9PSIsInZhbHVlIjoiZU5DQkhudG1Mb3NkbEsxOW1VV0hGeWY1Tzdxb2xHbVVrSE1BSmhxT2NyN2xwaEtHVmtcLzhJdkNxTksrMTFkMGQiLCJtYWMiOiIwNjQ3N2RlZmQ3ZTE4MTYwNjRkMTRjOWU4YmIwMjZjOWRmNzkwNjVmZmRkMjEzNDRiNzQ2Y2ZkODIwNGE2NDdhIn0%3D; _uetsid=cef8c4708dbb11eba992a3f9c16c24e0; _uetvid=cef906c08dbb11eb92672be3a9df9975",
    "referer": "https://toujoursmikes.ca/trouver-un-restaurant",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = {
    "Dimanche": "Sun",
    "Jeudi": "Thu",
    "Lundi": "Mon",
    "Mercredi": "Wed",
    "Samedi": "Sat",
    "Vendredi": "Fri",
    "Mardi": "Tue",
}


def fetch_data():
    locator_domain = "https://toujoursmikes.ca"
    json_url = "https://toujoursmikes.ca/service/search/branch?page=all&lang=fr"
    base_url = "https://toujoursmikes.ca/trouver-un-restaurant"
    with SgChrome() as driver:
        driver.get(base_url)
        exist = False
        while not exist:
            time.sleep(1)
            for rr in driver.requests:
                if rr.url == json_url and rr.response:
                    exist = True
                    locations = json.loads(rr.response.body)
                    for _ in locations:
                        hours = []
                        for key, val in _["schedule"]["week"].items():
                            times = ["closed"]
                            if val["counter"]["range"]:
                                times = val["counter"]["range"][0].values()
                            hours.append(f"{days[key]}: {'-'.join(times)}")
                        yield SgRecord(
                            page_url=_["links"]["self"],
                            store_number=_["id"],
                            location_name=_["title"],
                            street_address=_["address"]["address"],
                            city=_["address"]["city"],
                            state=_["address"]["province"],
                            latitude=_["lat"],
                            longitude=_["lng"],
                            phone=_["phone"],
                            zip_postal=_["address"]["zip"],
                            country_code=_["address"]["country"],
                            locator_domain=locator_domain,
                            hours_of_operation="; ".join(hours),
                        )
                    break


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
