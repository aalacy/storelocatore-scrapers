const storelocationsUS = 'https://www.johnstonmurphy.com/on/demandware.store/Sites-johnston-murphy-us-Site/en_US/Stores-SearchInternational?dwfrm_storelocator_address_country=US&dwfrm_storelocator_findbycountry=Search';
const storelocationsCA = 'https://www.johnstonmurphy.com/on/demandware.store/Sites-johnston-murphy-us-Site/en_US/Stores-FindStores?dwfrm_storelocator_address_country=CA&dwfrm_storelocator_findbycountry=Search';

const usLocationRequest = {
  url: storelocationsUS,
  userData: {
    urlType: 'initial',
    country: 'US',
  },
};
const canadaLocationRequest = {
  url: storelocationsCA,
  userData: {
    urlType: 'initial',
    country: 'CA',
  },
};

module.exports = {
  usLocationRequest,
  canadaLocationRequest,
};
