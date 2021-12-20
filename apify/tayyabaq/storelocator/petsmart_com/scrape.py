from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_types(types) -> str:
    tmp = []
    for t in types:
        s_type = t.get("displayName")
        tmp.append(s_type)
    location_type = ", ".join(tmp) or "<MISSING>"
    return location_type


def get_hours(hours) -> str:
    tmps = []
    for h in hours:
        day = h.get("day")
        time = h.get("time")
        line = f"{day} {time}"
        tmps.append(line)
    hours_of_operation = "; ".join(tmps) or "<MISSING>"
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.petsmart.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.petsmart.com/store-locator/",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "sentry-trace": "9d2f42b439f54872a05624b60cee7d0c-8b7748d654e6c17b-0",
        "Origin": "https://www.petsmart.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    data = {
        "dwfrm_storelocator_postalCode": "10001",
        "searchradius": "20000",
        "dwfrm_storelocator_distanceUnit": "mi",
        "dwfrm_storelocator_countryCode": "US",
        "dwfrm_storelocator_findbyzip": "Search",
        "omittConceptStores": "false",
        "uiData": '{"selectors":{"resultsSelectors":{"template":".store-information-template","target":"div#store-information","store":"li[data-results-storeId=\\"{{storeId}}\\"]","allStores":"data-results-storeid","mySavedStore":".my-saved-store"},"noResultsSelectors":{"template":".no-store-information-template","target":"div#no-store-information"},"resultsContent":"#stores-content","saveStoreButton":"button.btn-save-store","numberOfStores":"span.stores-count","formSelectors":{"searchTerm":"input[name=\'dwfrm_storelocator_postalCode\']","serviceFilterBoxes":"input.servicesfilter","serviceFiltersChecked":"input.servicesfilter:checkbox:checked","searchRadius":"select#searchradius","searchButton":"#storesearchbutton","searchForm":"form#storesearch"},"filter":{"label":"label.filter","spinningLabel":"label.filter.filter-spinner","servicesFilterContainer":".services-filter-container","selectAllButton":"a.select-all-services-button","servicesFilterCheckboxInput":"input[type=checkbox].servicesfilter"},"myStoreMasthead":"#masthead-my-store","dogLoader":".storelocator-init-dogloader","stickyWrapper":".sticky-wrapper","toggleServicesLink":"a.toggle-services","serviceToggle":".toggle-services span.toggle-stores-switch","map":{"storeLocatorMap":".store-locator-map","toggleMapLink":".toggle-map"}},"urls":{"getNearestStores":"/on/demandware.store/Sites-PetSmart-Site/default/StoreLocator-GetNearestStores"},"assetConfig":{"renderServices":true,"renderServicesButtons":true,"renderSaveStoreButton":true,"renderStoreHoursAsDailyLine":true}}',
        "context": "storelocator",
        "searchTriggerType": "interactive",
    }
    session = SgRequests()
    r = session.post(
        "https://www.petsmart.com/on/demandware.store/Sites-PetSmart-Site/default/StoreLocator-GetNearestStores",
        headers=headers,
        data=data,
    )

    js = r.json()["storeData"]["stores"]
    for j in js:
        slug = j.get("storeUrl")
        page_url = f"https://www.petsmart.com{slug}"
        a = j.get("address")
        location_name = a.get("name")
        types = j.get("services")
        location_type = get_types(types)
        street_address = f"{a.get('address1')} {a.get('address1')}".strip()
        state = a.get("stateCode") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = "US"
        city = a.get("city") or "<MISSING>"
        store_number = a.get("ID")
        latitude = j.get("latLon").get("lat") or "<MISSING>"
        longitude = j.get("latLon").get("lon") or "<MISSING>"
        phone = a.get("phone") or "<MISSING>"
        hours = j.get("hours") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            hours_of_operation = get_hours(hours)

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=street_address + " " + city + " " + state + " " + postal,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
