from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.static import static_coordinate_list, SearchableCountries
from sgrequests import SgRequests
from bs4 import BeautifulSoup


def write_output(data):
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        for row in data:
            writer.write_row(row)


def get(store, classname):
    component = store.find("span", class_=classname)
    return component.text.strip()


session = SgRequests()._session


def get_session(reset=False):
    global session
    if reset:
        session = SgRequests()._session
    return session


def fetch_with_retry(url, retry=0):
    try:
        headers = {
            "Host": "www.pearlevision.ca",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,ro;q=0.8",
            "Cookie": str(
                "".join(
                    [
                        "WC_AUTHENTICATION_-1002=-1002%2CCgQ64D1HPFU01Yzxj60dChBZ%2BEti%2B5IrxEDLfbZmZ4s%3D;",
                        "WC_ACTIVEPOINTER=-1%2C12551;",
                        "WC_USERACTIVITY_-1002=-1002%2C12551%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C1252615054%2CP8ZiPiAGNf1HQz74rFOoc7d7nJYHURPPuEe2QNFLN8jTC6IpNr%2Fwb51RHEuFQqbIeuKjKHPBHz4nKAoC%2FdKwi8Sn4nlb3xaiDddPNobq7LiDlDkowoWRwVvmESfxev86KUU8YlMATARtzFdAh7ZyW3ZAhrTx84Q04d3cwsGQqUJcSSnTnImvRhIHw3Q2ni5niEBYUcgxd5%2B1p5zXT4XsFgWZ9Kpr1UXFO93EjZ3or646NwmDeVPlwnolIVhtlnx%2F;",
                        "WC_GENERIC_ACTIVITYDATA=[7704303882%3Atrue%3Afalse%3A0%3A7jwOQd%2FuSznXc6UokPIn1G6P02WEZo1S7V3sRnNKtp4%3D][com.ibm.commerce.context.ExternalCartContext|null][com.ibm.commerce.context.entitlement.EntitlementContext|4000000000000002002%264000000000000002002%26null%26-2000%26null%26null%26null][com.ibm.commerce.store.facade.server.context.StoreGeoCodeContext|null%26null%26null%26null%26null%26null][com.ibm.commerce.catalog.businesscontext.CatalogContext|15952%26null%26false%26false%26false][CTXSETNAME|Store][com.ibm.commerce.context.base.BaseContext|12551%26-1002%26-1002%26-1][com.ibm.commerce.context.audit.AuditContext|1604840324929-222938][com.ibm.commerce.context.experiment.ExperimentContext|null][com.ibm.commerce.giftcenter.context.GiftCenterContext|null%26null%26null][com.ibm.commerce.context.globalization.GlobalizationContext|-1%26CAD%26-1%26CAD];",
                    ]
                )
            ),
        }

        res = session.get(url, headers=headers, timeout=100)
        return res
    except Exception as e:
        if retry < 3:
            return fetch_with_retry(url, retry + 1)
        else:
            raise e


def fetch_data():
    coords = static_coordinate_list(10, country_code=SearchableCountries.CANADA)

    for lat, lng in coords:
        url = f"https://www.pearlevision.ca/webapp/wcs/stores/servlet/AjaxStoreLocatorResultsView?resultSize=5000&latitude={lat}&longitude={lng}"

        res = fetch_with_retry(url)

        soup = BeautifulSoup(res.text, "html.parser")
        stores = soup.find_all("div", class_="store-data")

        for store in stores:
            locator_domain = "pearlevision.ca"
            location_name = get(store, "storeName")
            store_number = get(store, "storeNumber")
            page_url = get(store, "website")

            street_address = get(store, "address")
            city = get(store, "city")
            state = get(store, "state")
            postal = get(store, "zipCode")

            phone = get(store, "phone")
            latitude = get(store, "latitude")
            longitude = get(store, "longitude")
            hours_of_operation = get(store, "hours")

            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="US",
                store_number=store_number,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
