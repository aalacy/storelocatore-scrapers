import usaddress
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://siteassets.parastorage.com/pages/pages/thunderbolt?beckyExperiments=specs.thunderbolt.addressInputAtlasProvider%3Atrue%2Cspecs.thunderbolt.seoFriendlyDropDownMenu%3Atrue%2Cspecs.thunderbolt.FileUploaderPopper%3Atrue%2Cspecs.thunderbolt.image_placeholder%3Atrue%2Cdm_inputFixerNotAddData%3Atrue%2Ctb_UploadButtonFixValidationNotRequired%3Atrue%2Cspecs.thunderbolt.componentsRegistry%3Atrue%2Cspecs.thunderbolt.breakingBekyCache%3Atrue%2Cspecs.thunderbolt.tb_media_layout_by_effect%3Atrue&contentType=application%2Fjson&deviceType=Desktop&dfCk=6&dfVersion=1.1393.0&experiments=bv_cartPageResponsiveLayoutFixer%2Cbv_migrateResponsiveToVariantsModels%2Cbv_removeMenuDataFromPageJson%2Cbv_remove_add_chat_viewer_fixer%2Cdm_fixMobileSplitDesign%2Cdm_keepChildlessAppWidget%2Cdm_migrateToTextTheme%2Cdm_removeResponsiveDataFromClassicEditorFixer&externalBaseUrl=https%3A%2F%2Fwww.spadstwisters.com&fileId=33181c1a.bundle.min&hasTPAWorkerOnSite=false&isHttps=true&isInSeo=false&isMultilingualEnabled=false&isPremiumDomain=true&isUrlMigrated=true&isWixCodeOnPage=false&isWixCodeOnSite=false&language=en&languageResolutionMethod=QueryParam&metaSiteId=bb8df256-69e7-4a35-a811-6ef5264dbe40&module=thunderbolt-features&originalLanguage=en&pageId=a9ebb0_4d6b3c31a9a8582869dcdb35ee33c650_113.json&quickActionsMenuEnabled=false&registryLibrariesTopology=%5B%7B%22artifactId%22%3A%22editor-elements%22%2C%22namespace%22%3A%22wixui%22%2C%22url%22%3A%22https%3A%2F%2Fstatic.parastorage.com%2Fservices%2Feditor-elements%2F1.6424.0%22%7D%2C%7B%22artifactId%22%3A%22editor-elements%22%2C%22namespace%22%3A%22dsgnsys%22%2C%22url%22%3A%22https%3A%2F%2Fstatic.parastorage.com%2Fservices%2Feditor-elements%2F1.6424.0%22%7D%5D&remoteWidgetStructureBuilderVersion=1.226.0&siteId=1f5eab97-bcd6-46c1-aaf5-60c05b1b1442&siteRevision=113&staticHTMLComponentUrl=https%3A%2F%2Fwww-spadstwisters-com.filesusr.com%2F&useSandboxInHTMLComp=false&viewMode=desktop"
    session = SgRequests()
    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "BuildingName": "address2",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["props"]["render"]["compProps"]["comp-iz95ryrn"]["images"]
    for j in js:

        page_url = "https://www.spadstwisters.com/locations"
        location_name = j.get("title")
        info = "".join(j.get("description")).split("\n")
        ad = " ".join("".join(j.get("description")).split("\n")[:2])
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "USA"
        city = a.get("city") or "<MISSING>"
        try:
            text = "".join(j.get("href"))
        except:
            text = "<MISSING>"
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "<MISSING>"
        if len(info) > 3:
            phone = info[2]
        hours_of_operation = info[-1]
        if len(info) > 4:
            hours_of_operation = " ".join(info[3:])
        if hours_of_operation.find("Temporarily closed") != -1:
            hours_of_operation = "Temporarily closed"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.spadstwisters.com"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
