const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');


var url= "http://weingartenrealty.propertycapsule.com/cre/commercial-real-estate-listings-portfolio"

 
 
async function scrape(){
  return new Promise(async (resolve,reject)=>{
request(url,(err,res,html)=>{
                    if(!err && res.statusCode==200){
                      
                          const $  =cheerio.load(html);
                           
                          var items=[];
 
                                     main = $('#pc-property-list').find('tbody').find('tr').find('a');//.attr('href');
                                     function mainhead(i)

                                     {
                                         if(main.length>i)
           
                                             {
                                       var link =  $('#pc-property-list').find('tbody').find('tr').find('a').eq(i).attr('href');
                                       request(link,(err,res,html)=>{
                                        if(!err && res.statusCode==200){
                                          
                                              const $  =cheerio.load(html);
                                              var location_name = $('.floated-4').find('.property-metadata').text();
                                              var address_tmp = $('.floated-4').find('.p-street-address').text();
                                              if(address_tmp!=''){
                                                var address = $('.floated-4').find('.p-street-address').text();
                                              }
                                              else {
                                                var address = $('.floated-4').find('.p-market').text();
                                              }
                                              
                                              var city = $('.floated-4').find('.p-locality').text();
                                              var state_tmp =$('.floated-4').find('.p-region').text().trim().split('Directions');
                                              var phone_tmp = $('.h-card:nth-child(2)').find('.p-tel').text();
                                              if(phone_tmp!=''){
                                                var phone = $('.h-card:nth-child(2)').find('.p-tel').text();
                                              }
                                              else {
                                                var phone ='<MISSING>';
                                              }
                                             
                                              var state_tmp1 = state_tmp[0].trim().split(' ');
                                              var latitude_tmp = state_tmp[1].trim().split(',');
                                               if (latitude_tmp.length ==2){
                                                 var latitude = latitude_tmp[0];
                                                 var longitude = latitude_tmp[0];

                                               }
                                               else if(latitude_tmp.length ==1){
                                                var latitude = '<MISSING>';
                                                var longitude = '<MISSING>';

                                               }
                                              
                                              if (state_tmp1.length ==2){
                                                var state = state_tmp1[0];
                                                var zip = state_tmp1[1];

                                              }
                                              else if(state_tmp1.length==1){
                                                var state = state_tmp1[0];
                                                var zip = '<MISSING>';
                                              }
                                              
                                              items.push({  

                                                locator_domain: 'http://weingartenrealty.propertycapsule.com/', 
                
                                                location_name: location_name, 
                                    
                                                street_address: address,
                                    
                                                city: city, 
                                    
                                                state: state,
                                    
                                                zip:  zip,
                                    
                                                country_code: 'US',
                                    
                                                store_number: '<MISSING>',
                                    
                                                phone: phone,
                                    
                                                location_type: 'weingartenrealty',
                                    
                                                latitude: latitude,
                                    
                                                longitude: longitude, 
                                    
                                                hours_of_operation: '<MISSING>'});
                                                mainhead(i+1);
                                        }
                                      });
                                       
                                     
                                     
                              
                                    }
                                          
                                          
                                    else{
                                
                                    resolve(items);
                                
                                    }
                              } 
            
                              mainhead(1);                    
                        
  }
 
 });
})
}
  
Apify.main(async () => {

    

    const data = await scrape();
   
     await Apify.pushData(data);
    
  
  });
