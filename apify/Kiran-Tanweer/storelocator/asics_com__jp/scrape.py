from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
import os

os.environ["PROXY_URL"] = "http://groups-BUYPROXIES94952:{}@proxy.apify.com:8000/"
os.environ["PROXY_PASSWORD"] = "apify_proxy_4j1h689adHSx69RtQ9p5ZbfmGA3kw12p0N2q"


session = SgRequests()
website = "asics_com__jp"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Cookie": "_abck=BDC85DE3F8EE8549936F9CCA6E91F9F2~-1~YAAQnL3XF94Q5Hl+AQAAYxSSkQcLIpXXJQsg94tR78O31VM/LJkruLwy1FuIAqO+ycJ04nbxd0ZtjKLvGtn58yntHBqhZDzEPKYe1Iwe9KAMK7V39hMjubNoKx+yiDvvQiMuNtw7s5QivFZjpfZ/nA+JEtR/7tHGGNYQFI57CBeuxMSsJiitvHsrybtXe4nJpeQBoimG3QSf1a2ChDwOHIkTLsYGwCqZnftV8tWVogvT9vpKqMWcXiKNjml+2FpdromV29w8C3q60ezdVJEXscXFf3MMQdZXg9MjVMcUfIkuok74VonZf29rm11BhsMDruOn62SHo0rGg+n93nAQC3MXOd4ym5HUGu4xvs74nSzdMy9mbMilmvA1TJ+KTT85VMuaw/EllIJhJvLqdXv/v3eveuhu60iA~0~-1~-1; ak_bmsc=9E2B8BB7B0A00008378D025E2C68AE03~000000000000000000000000000000~YAAQnL3XF98Q5Hl+AQAAYxSSkQ4CXILOYRG6j2TTjVoc5Uw9VEO9a3kcKDWxTWn2ty+z92LBrBlH1mEcs8oUWBnrD/m+UKgc1vRdH1WYOmCAG+GU1n0RxTiVUxBDRi59Szj11owj2zdzVlHiviSOttre1eLCH/mPS10NKLbJ9AmjzC5OfGuJochZza8sfEs38Q5zsSnGBR5SEwHDnYWJVvpTYkIF+46GiBd0y7Gzg2XWkfOqBdBjlFjCRsR3sKCKpMKgRfZct3ny2I675dxZfjF4YezALmoiHsOPXAe05NTElonExv8paiBWNhT6qCW5CHl8vNMuEbMEn3LfKRYE3JUQonAMs7cDZDQoizCLYk2GiAGNP9sBL5wkeAZ11i4JSzKsRtynQ6LSV12kFAoxtULd11HOKvbjLOV/by0NwsbxITf2fu9F7tDg2FJGKpqPBOSnEPp6x19n4TZN4P5P51cLHftD/QVba2B0uMrkNdLGzF64DZdSPhoVbBZ1GtD2A25TTPeBsQ==; bm_sv=B3B91B7A83843C4FD11EF09306269C64~cWXJbE6SSXyY8cXanbiIX6HVoNc1UoxyTOetP1J309eFs+gqJ+TIZzquNIhGl5JZx64Z6CLk79hCyaQc7XJbcFEMc2g0ssrzNAPJHiR6DaW4sxppS1dsoNZ3wU1XU8WpiPPPY5BD37DSu+73V24VDQixpS7xVQ2ydclKoP5q8Z0=; bm_sz=4AF2A28D15E036D7C707E9B8172BD313~YAAQnL3XF1wS5Hl+AQAAbVGSkQ4pbpYTqDytaUet1BsLM2sZtHozPQdbDHA5rtW1A4fKYXFGvg2SclmOHY7CxLK8Wlgp7cyF8ZoEQQvZLDM7p8IVAtzjY/BQpMBWlvKjuGBM4DRwAjni4PnxVNUmBF6eq2e6vz/O6Mw7LRaBF1TKnYMpF6jHqwTp6NHb6qLAfBSJ89QSnqDTzPxexq9X4iaCzXEDpokUt0aGJhJuZcNbTx8Fa+qPTKQyWUcDT0ZibpgK+uL8C+bdTUE1OZFXq3L/1rS81bGOxhO+vI6YKWzJtQ==~3753523~3228485; locale=ja-jp; user_country=PK"
}


DOMAIN = "https://www.asics.com/jp"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "https://www.asics.com/jp/ja-jp/store-locator.json?per-page=10000"
        req = session.get(search_url, headers=headers).json()
        for store in req["Stores"]:
            loc = req["Stores"][store]
            storeid = loc["ID"]
            title = loc["Title"]
            street = loc["Address"]
            city = loc["City"]
            region = loc["Region"]
            pcode = loc["Postcode"]
            phone = loc["Phone"]
            lat = loc["Latitude"]
            lng = loc["Longitude"]
            url = "https://www.asics.com" + loc["URL"]
            loc_type = loc["StoreType"]

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=region.strip(),
                zip_postal=pcode,
                country_code="JP",
                store_number=storeid,
                phone=phone,
                location_type=loc_type,
                latitude=lat,
                longitude=lng,
                hours_of_operation=MISSING,
            )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID({SgRecord.Headers.LATITUDE, SgRecord.Headers.LONGITUDE})
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
