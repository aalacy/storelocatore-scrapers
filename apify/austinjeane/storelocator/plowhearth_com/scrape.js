const Apify = require('apify');
const axios = require('axios');

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

async function scrape() {
    var rawStores = [];

    var itemsInPage = null;
    var currentPage = 0;
    do {
        var response = await axios.get('https://www.plowhearth.com/en/store-finder?q=27103&page=' + currentPage);
        response.data.data.forEach((store) => rawStores.push(store));
        itemsInPage = response.data.total;
        currentPage++;
      }
      while (itemsInPage !== 0);
    
      for (let i = 0; i < rawStores.length; i++) {
          const store = rawStores[i];
          if(store.openings) {
              store.hours = `Sun: ${store.openings.Sun}. Mon: ${store.openings.Mon}. Tue: ${store.openings.Tue}. Wed: ${store.openings.Wed}. Thu: ${store.openings.Thu}. Fri: ${store.openings.Fri}. Sat: ${store.openings.Sat}.`
          }
      }

    var stores = rawStores.map(store => ({
        locator_domain: 'plowhearth.com',
        location_name: store.displayName,
        street_address: store.line1 + ' ' +store.line2,
        city: store.town,
        state: store.state,
        zip: store.postalCode,
        country_code: 'US',
        store_number: store.name,
        phone: store.phone,
        location_type: store.name,
        latitude: parseFloat(store.latitude),
        longitude: parseFloat(store.longitude),
        hours_of_operation: store.hours.replace(/<[^>]*>?/gm, ' '),
    }));


    return stores;

}
