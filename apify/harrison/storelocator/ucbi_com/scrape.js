const Apify = require('apify');
const axios = require('axios');

async function scrape() {
    stores = []
    let res = await axios.get('https://www.ucbi.com/LocationsService.svc/GetLocations?lat=0&lng=0&radius=0');
    for (let store of res.data.List) {
        let s = {
          locator_domain: 'https://www.ucbi.com/',
          location_name: store.Name,
          street_address: store.Address1,
          city: store.City,
          state: store.State,
          zip: store.Zip,
          country_code: 'US',
          store_number: store.LocationId,
          phone: store.Phone,
          location_type: null,
          niacs_code: null,
          latitude: store.Latitude,
          longitude: store.Longitude,
          external_lat_long: false,
          hours_of_operation: null,
        }
        if(store.StoreHours) {
              s.hours_of_operation = store.StoreHours.replace(`\\`, '').replace(`"`, '').replace(`"`, '');
        }
        stores.push(s);
    }
    return stores;
}

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});
