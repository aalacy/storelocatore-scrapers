const Apify = require('apify');
const request = require('request-promise');
const {xml2js} = require('xml-js');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  // Begin scraper
  const rootAddress = 'https://hosted.where2getit.com/kicksusa/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E50BFE3AA-63AE-11E4-8806-5889F3F215A2%3C%2Fappkey%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Climit%3E250%3C%2Flimit%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3E%3C%2Faddressline%3E%3Clongitude%3E-77.03613281249997%3C%2Flongitude%3E%3Clatitude%3E39.19820534889479%3C%2Flatitude%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Csearchradius%3E1054.3095703124998%3C%2Fsearchradius%3E%3C%2Fformdata%3E%3C%2Frequest%3E';
  const records = [];

  const xmlResponse = await request.get(rootAddress);
  pois = xml2js(xmlResponse, {
    compact: true,
    trim: true,
    // ignoreDeclaration: true,
    // ignoreInstruction: true,
    // ignoreAttributes: true,
    // ignoreComment: true,
    // ignoreCdata: true,
    // ignoreDoctype: true
  }).response.collection.poi

  for (const poi of pois) {
    records.push({
      locator_domain: 'kicksusa.com',
      location_name: poi.name._text,
      street_address: `${poi.address1._text} ${poi.address2._text}`,
      city: poi.city._text,
      state: poi.state._text,
      zip: poi.postalcode._text,
      country_code: poi.country._text,
      store_number: poi.clientkey._text,
      phone: poi.phone._text,
      location_type: '<MISSING>',
      latitude: poi.latitude._text,
      longitude: poi.longitude._text,
      hours_of_operation: `Sunday: ${poi.sun._text} Monday: ${poi.mon._text} Tuesday: ${poi.tues._text} Wednesday: ${poi.wed._text} Thursday: ${poi.thurs._text} Friday: ${poi.fri._text} Saturday: ${poi.sat._text}`
    })
  }

	return records;

	// End scraper

}
