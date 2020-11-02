const Apify = require('apify');
const request = require('request-promise');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  // Begin scraper
  const records = [];
  const data = JSON.parse(await request.get({
    url:'https://cdn.storelocatorwidgets.com/json/178ecac2bff5d20c4041ada5f817d79e?callback=slw&_=1565878371236',
    gzip: true
  }).then(body => { return body.slice(4,-1); }));

  for (const store of data.stores) {
    try {
      var { location_name, street_address, city, state, zip } = store.data.address.match(
        /((?<location_name>.+)[\r\n]+)?(?<street_address>.+)[\r\n]+(?<city>.+),\s(?<state>[A-Z]{2})\s(?<zip>[\d-]{5,})/
      ).groups
    } catch (error) {
      if (store.data.address.indexOf('Closed') !== -1) {
        continue
      }
      throw error
    }

    records.push({
      locator_domain: 'salsitalianristorante.com',
      location_name: location_name || store.name,
      street_address,
      city,
      state,
      zip,
      country_code: 'US',
      store_number: store.storeid,
      phone: store.data.phone,
      location_type: '<MISSING>',
      latitude: store.data.map_lat,
      longitude: store.data.map_lng,
      hours_of_operation: JSON.stringify((({ hours_Sunday, hours_Monday, hours_Tuesday, hours_Wednesday, hours_Thursday, hours_Friday, hours_Saturday }) => {return { hours_Sunday, hours_Monday, hours_Tuesday, hours_Wednesday, hours_Thursday, hours_Friday, hours_Saturday }})(store.data)),
    });
  }


	return records;

	// End scraper

}
