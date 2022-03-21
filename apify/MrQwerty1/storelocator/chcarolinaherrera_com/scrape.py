import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode or SgRecord.MISSING

    return street_address, city, state, postal


def get_urls():
    params = set()
    r = session.get("https://chcarolinaherrera.com/00/en/storelocator")
    tree = html.fromstring(r.text)
    countries = tree.xpath("//datalist")
    for country in countries:
        code = "".join(country.xpath("./@data-country-id"))
        states = country.xpath("./option/@value")
        for state in states:
            params.add((code, state))

    return params


def get_data(param, sgw: SgWriter):
    country_code, state_code = param
    params = (
        ("langId", "-1002"),
        ("country", country_code),
        ("state", state_code),
        ("searchTerm", ""),
    )
    api = "https://chcarolinaherrera.com/STLStoreLocatorJSONDisplayView"
    r = session.get(api, cookies=cookies, params=params)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script/text()"))
    try:
        text = "[" + text.split("= [")[1].split("];")[0].replace("'", '"') + "]"
    except IndexError:
        return
    js = json.loads(text)

    for j in js:
        location_name = j.get("name")
        raw_address = ", ".join(j.get("address") or []).strip()
        street_address, city, state, postal = get_international(raw_address)
        if postal == SgRecord.MISSING and country_code == "US":
            street_address = raw_address.split(",")[0].strip()
            city = raw_address.split(",")[1].strip()
            postal = raw_address.split(",")[2].strip()
        phone = j.get("telf") or ""
        phone = phone.lower().replace("n/d", "").strip()
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        store_number = j.get("id")

        _tmp = []
        hours = j.get("timetable") or []
        for h in hours:
            day = h.get("day")
            inter = h.get("hours")
            _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=SgRecord.MISSING,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    params = list(get_urls())

    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {
            executor.submit(get_data, param, sgw): param for param in params
        }
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://chcarolinaherrera.com/"
    session = SgRequests()
    cookies = {
        "WC_ACTIVEPOINTER": "-1002%2C715838508",
        "WC_USERACTIVITY_-1002": "-1002%2C715838508%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C1276934683%2CGX40%2Beo%2BoNwf08%2Fu6mx0K%2FVWL%2BSn546sSb6BJKAFxPCr%2BEjGtdTIvX99uR2twU5rTfFLlRLu4nJC3kMw380aH7VpjuVcjyRQFWkhJKfafkNiAPxZ7weuQCHPWBsufgPge6iPBgAx8IWnDQ7v9fOugrIiEHAlHlEjAqIvAd9Tb7dP51tqtC4WFlpmmaMhXiuWGDXEAhEr1hlMbokwF%2FMOzZYn4xKpu0yTowdvFCgjCU3sCwzeo2liwKxq7K8U94o4",
        "WC_GENERIC_ACTIVITYDATA": "[304377056%3Atrue%3Afalse%3A0%3Ah47lXJ3uD2D5zBok%2Bw9rraZpbjwY2q0%2B%2Bf8RR%2FdWl4M%3D][com.ibm.commerce.context.ExternalCartContext|null][com.ibm.commerce.context.entitlement.EntitlementContext|null%26null%26null%26-2000%26null%26null%26null][com.ibm.commerce.store.facade.server.context.StoreGeoCodeContext|null%26null%26null%26null%26null%26null][com.ibm.commerce.catalog.businesscontext.CatalogContext|3074457345616676668%26null%26false%26false%26false][CTXSETNAME|Store][com.ibm.commerce.context.base.BaseContext|715838508%26-1002%26-1002%26-1][com.ibm.commerce.context.audit.AuditContext|1629725810648-49940][com.ibm.commerce.context.experiment.ExperimentContext|null][com.ibm.commerce.giftcenter.context.GiftCenterContext|null%26null%26null][com.ibm.commerce.context.globalization.GlobalizationContext|-1002%26EUR%26-1002%26EUR]",
    }
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
