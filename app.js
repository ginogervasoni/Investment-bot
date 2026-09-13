const zones = [
  {id:'candioti-norte',name:'Candioti Norte',type:'Consolidada · Residencial mixta',lat:-31.625,lng:-60.690,base:82,price:1580,yield:5.9,growth:8.4,development:76,risk:21,demand:88,infrastructure:92,observations:124,delta:6,drivers:[['Demanda de alquiler',92],['Conectividad y servicios',88],['Actividad comercial',79]],history:[76,77,77,78,79,78,80,80,81,81,82,82]},
  {id:'centro',name:'Centro',type:'Consolidada · Alta densidad',lat:-31.648,lng:-60.710,base:77,price:1320,yield:6.5,growth:4.9,development:71,risk:27,demand:90,infrastructure:96,observations:210,delta:2,drivers:[['Liquidez del mercado',94],['Servicios urbanos',92],['Oferta de alquiler',85]],history:[75,75,76,75,76,77,77,76,77,77,77,77]},
  {id:'constituyentes',name:'Constituyentes',type:'Consolidada · Residencial',lat:-31.636,lng:-60.716,base:74,price:1180,yield:6.7,growth:6.8,development:64,risk:25,demand:82,infrastructure:86,observations:98,delta:5,drivers:[['Precio relativo',86],['Demanda residencial',81],['Cercanía al centro',78]],history:[69,70,70,71,72,72,73,72,73,74,74,74]},
  {id:'guadalupe',name:'Guadalupe',type:'Consolidada · Residencial',lat:-31.602,lng:-60.682,base:73,price:1100,yield:5.6,growth:7.6,development:62,risk:24,demand:79,infrastructure:83,observations:87,delta:7,drivers:[['Calidad residencial',85],['Valorización reciente',82],['Acceso a espacios verdes',76]],history:[66,67,68,68,69,70,71,70,72,72,73,73]},
  {id:'puerto',name:'Puerto / Dique II',type:'Emergente · Usos mixtos',lat:-31.653,lng:-60.700,base:72,price:1690,yield:4.8,growth:9.5,development:89,risk:39,demand:69,infrastructure:79,observations:54,delta:9,drivers:[['Nuevos desarrollos',95],['Transformación urbana',90],['Oferta premium',72]],history:[63,64,65,65,67,68,69,69,70,71,72,72]},
  {id:'candioti-sur',name:'Candioti Sur',type:'Consolidada · Residencial mixta',lat:-31.637,lng:-60.697,base:70,price:1250,yield:6.1,growth:5.7,development:68,risk:29,demand:80,infrastructure:88,observations:103,delta:3,drivers:[['Accesibilidad',87],['Demanda estable',80],['Precio competitivo',74]],history:[67,68,68,68,69,69,69,70,69,70,70,70]},
  {id:'barranquitas',name:'Barranquitas',type:'Emergente · Residencial',lat:-31.642,lng:-60.738,base:64,price:690,yield:7.4,growth:7.2,development:58,risk:47,demand:66,infrastructure:61,observations:61,delta:8,drivers:[['Precio de entrada',92],['Rentabilidad potencial',88],['Mejora de conectividad',68]],history:[56,57,58,59,59,60,61,62,62,63,64,64]},
  {id:'nueva-pompeya',name:'Nueva Pompeya',type:'Emergente · Residencial',lat:-31.610,lng:-60.718,base:59,price:620,yield:7.1,growth:5.8,development:55,risk:52,demand:61,infrastructure:57,observations:43,delta:5,drivers:[['Precio accesible',91],['Demanda local',65],['Suelo disponible',63]],history:[54,54,55,56,56,57,57,58,58,59,59,59]},
  {id:'colastine-norte',name:'Colastiné Norte',type:'Expansión · Residencial',lat:-31.633,lng:-60.595,base:55,price:870,yield:4.5,growth:6.9,development:61,risk:71,demand:58,infrastructure:49,observations:37,delta:1,drivers:[['Expansión residencial',78],['Entorno natural',74],['Disponibilidad de suelo',69]],history:[54,55,55,56,55,55,56,56,55,55,56,55]},
  {id:'alto-verde',name:'Alto Verde',type:'En desarrollo · Residencial',lat:-31.668,lng:-60.674,base:41,price:480,yield:6.8,growth:3.2,development:42,risk:79,demand:49,infrastructure:38,observations:22,delta:-2,drivers:[['Precio de entrada',88],['Proximidad urbana',58],['Demanda local',52]],history:[43,43,42,43,42,42,42,41,42,41,41,41]}
];

const profiles={balanced:{demand:.30,development:.25,infrastructure:.20,yield:.15,growth:.10,risk:.18},rent:{demand:.32,development:.08,infrastructure:.20,yield:.30,growth:.10,risk:.20},growth:{demand:.24,development:.25,infrastructure:.16,yield:.08,growth:.27,risk:.18},development:{demand:.18,development:.38,infrastructure:.18,yield:.06,growth:.20,risk:.20},conservative:{demand:.27,development:.12,infrastructure:.28,yield:.16,growth:.07,risk:.32}};
const state={metric:'score',strategy:'balanced',minScore:45,selected:'candioti-norte',compare:[]};
let map,markers=new Map(),officialBoundaries,censusLayer,censusData,constructionData,marketData,meliData,affordabilityData,pipelineData;

const $=s=>document.querySelector(s); const $$=s=>[...document.querySelectorAll(s)];
const fmt=n=>new Intl.NumberFormat('es-AR').format(n);
const money=n=>new Intl.NumberFormat('es-AR',{style:'currency',currency:'ARS',maximumFractionDigits:0}).format(n);
const pct=n=>`${n>=0?'+':''}${n.toFixed(1).replace('.',',')}%`;
const periodLabel=period=>{const [year,month]=period.split('-').map(Number);return new Intl.DateTimeFormat('es-AR',{month:'short',year:'numeric'}).format(new Date(year,month-1,1)).replace('.','')};
const quarterLabel=period=>{const [year,quarter]=period.split('-Q');return `${quarter}º trim ${year}`};
const MARKET_REMOTE_URL='https://raw.githubusercontent.com/ginogervasoni/Investment-bot/main/data/market-santa-fe.json';
const CONSTRUCTION_REMOTE_URL='https://raw.githubusercontent.com/ginogervasoni/Investment-bot/main/data/construction-series.json';
const AFFORDABILITY_REMOTE_URL='https://raw.githubusercontent.com/ginogervasoni/Investment-bot/main/data/affordability-santa-fe.json';
const PIPELINE_REMOTE_URL='https://raw.githubusercontent.com/ginogervasoni/Investment-bot/main/data/pipeline-status.json';
const MELI_REMOTE_URL='https://raw.githubusercontent.com/ginogervasoni/Investment-bot/main/data/mercadolibre-santa-fe.json';

function validMarketPayload(data){
  const city=data?.city,zones=data?.zones;
  return data?.attribution==='Fuente: TuLugar (tulugar.com)'&&city&&zones&&Number.isFinite(city.listings_total)&&city.listings_total===city.listings_sale+city.listings_rent&&Object.keys(zones).length>0;
}

function validMeliPayload(data){
  if(data?.schema_version!=='1.0'||data?.source?.publisher!=='Mercado Libre')return false;
  if(['pending_authorization','pending_credentials_check'].includes(data.status))return data.city===null&&data.zones&&Object.keys(data.zones).length===0;
  return data.status==='active'&&data.city&&Number.isFinite(data.city.listings)&&data.city.listings>0&&Number.isFinite(data.city.sample_with_area);
}

async function loadMeliData(){
  try{
    let response;
    try{response=await fetch(`${MELI_REMOTE_URL}?v=${Date.now()}`,{cache:'no-store'});if(!response.ok)throw new Error(`HTTP ${response.status}`);meliData=await response.json();if(!validMeliPayload(meliData))throw new Error('Datos remotos inválidos')}
    catch(remoteError){response=await fetch('data/mercadolibre-santa-fe.json');if(!response.ok)throw new Error(`HTTP ${response.status}`);meliData=await response.json();if(!validMeliPayload(meliData))throw new Error('Datos locales inválidos')}
    renderMeliMarket();
  }catch(error){console.error('No se pudo cargar Mercado Libre',error);$('#meliState').className='meli-state error';$('#meliState').innerHTML='<i></i>Conector no disponible';$('#meliIntro').textContent='No fue posible verificar el estado del conector.'}
}

function renderMeliMarket(){
  const state=$('#meliState'),intro=$('#meliIntro'),kpis=$('#meliKpis');
  if(meliData.status!=='active'){
    state.className='meli-state pending';state.innerHTML='<i></i>Pendiente de OAuth';kpis.hidden=true;
    intro.textContent='La aplicación ya está creada y sus credenciales están protegidas. Falta autorizar la cuenta mediante Authorization Code OAuth antes de consultar la API.';
    $('#meliUpdated').textContent='Sin datos hasta completar OAuth';return;
  }
  const city=meliData.city;
  state.className='meli-state active';state.innerHTML='<i></i>API activa';kpis.hidden=false;
  intro.textContent='Cobertura complementaria de departamentos publicados en venta. Se procesa por separado para no mezclar metodologías ni contar avisos como operaciones cerradas.';
  $('#meliListings').textContent=fmt(city.listings);$('#meliAreaSample').textContent=fmt(city.sample_with_area);
  $('#meliMedianSale').textContent=city.median_sale_usd?`US$ ${fmt(Math.round(city.median_sale_usd))}`:'Sin muestra';
  $('#meliMedianM2').textContent=city.median_apartment_price_usd_m2?`US$ ${fmt(Math.round(city.median_apartment_price_usd_m2))}`:'Sin muestra';
  $('#meliUpdated').textContent=`API MLA · ${city.snapshot_date.split('-').reverse().join('/')} · ${Object.keys(meliData.zones).length} zonas verificadas`;
}

async function loadConstructionData(){
  try{
    let response;
    try{response=await fetch(`${CONSTRUCTION_REMOTE_URL}?v=${Date.now()}`,{cache:'no-store'});if(!response.ok)throw new Error(`HTTP ${response.status}`);constructionData=await response.json();if(constructionData?.schema_version!=='1.0')throw new Error('Datos remotos inválidos')}
    catch(remoteError){response=await fetch('data/construction-series.json');if(!response.ok)throw new Error(`HTTP ${response.status}`);constructionData=await response.json();if(constructionData?.schema_version!=='1.0')throw new Error('Datos locales inválidos')}
    renderConstruction();
  }catch(error){console.error('No se pudo cargar la serie de construcción',error);$('#constructionCost').textContent='No disponible';$('#constructionUpdated').textContent='No fue posible cargar la serie oficial.'}
}

async function loadMarketData(){
  try{
    let response;
    try{response=await fetch(`${MARKET_REMOTE_URL}?v=${Date.now()}`,{cache:'no-store'});if(!response.ok)throw new Error(`HTTP ${response.status}`);marketData=await response.json();if(!validMarketPayload(marketData))throw new Error('Datos remotos inválidos')}
    catch(remoteError){response=await fetch('data/market-santa-fe.json');if(!response.ok)throw new Error(`HTTP ${response.status}`);marketData=await response.json();if(!validMarketPayload(marketData))throw new Error('Datos locales inválidos')}
    renderMarketOverview();updateZoneMarket(zones.find(z=>z.id===state.selected));if(state.metric==='market')applyMapMode();
  }catch(error){console.error('No se pudo cargar el mercado',error);$('#marketZoneTitle').textContent='Mercado no disponible';$('#marketTable').innerHTML='<p>No fue posible cargar los datos del mercado.</p>'}
}

function marketForZone(z){return marketData?.zones?.[z.id]}
function marketColor(value){if(value==null)return '#89969f';return value>=2000?'#175f4a':value>=1700?'#239669':value>=1400?'#53b889':value>=1000?'#e6b94c':'#e88935'}
function updateZoneMarket(z){
  const market=marketForZone(z),source=$('#marketZoneSource');
  if(!market){$('#marketZoneTitle').textContent='Sin coincidencia territorial válida';['#marketPrice','#marketRent','#marketSale','#marketListings'].forEach(id=>$(id).textContent='—');source.href='https://tulugar.com/es/datos';return}
  $('#marketZoneTitle').textContent=`${market.source_neighborhood} · ${periodLabel(market.period)}`;$('#marketPrice').textContent=`US$ ${fmt(Math.round(market.apartment_price_usd_m2))}`;$('#marketRent').textContent=market.median_rent_usd_month?`US$ ${fmt(Math.round(market.median_rent_usd_month))}`:'Sin muestra';$('#marketSale').textContent=`US$ ${fmt(Math.round(market.median_sale_usd))}`;$('#marketListings').textContent=fmt(market.listings_total);source.href=market.source_page;
}

function renderMarketOverview(){
  const city=marketData.city;$('#marketCityListings').textContent=fmt(city.listings_total);$('#marketCitySaleListings').textContent=fmt(city.listings_sale);$('#marketCityRentListings').textContent=fmt(city.listings_rent);$('#marketCitySale').textContent=`US$ ${fmt(Math.round(city.median_sale_usd))}`;$('#marketCityRent').textContent=`US$ ${fmt(Math.round(city.median_rent_usd_month))}`;$('#marketSnapshotDate').textContent=`Santa Fe Capital · ${city.snapshot_date.split('-').reverse().join('/')}`;$('#marketUpdated').textContent=`Fuente: TuLugar · snapshot ${city.snapshot_date.split('-').reverse().join('/')}`;
  const rows=Object.entries(marketData.zones).sort(([,a],[,b])=>b.apartment_price_usd_m2-a.apartment_price_usd_m2);
  const latestPeriod=rows.map(([,row])=>row.period).sort().at(-1),generated=new Date(`${marketData.generated_at}T00:00:00Z`),ageDays=Math.max(0,Math.floor((Date.now()-generated.getTime())/86400000)),now=new Date(),nextCheck=new Date(now.getFullYear(),now.getMonth()+1,1);
  $('#marketPeriodLabel').textContent=periodLabel(latestPeriod);$('#pipelineStatus').textContent='Automatización activa';$('#pipelineLastUpdate').textContent=marketData.generated_at.split('-').reverse().join('/');$('#pipelineFreshness').textContent=ageDays<=45?'Datos dentro del ciclo mensual':`Última actualización hace ${ageDays} días`;$('#pipelineNextCheck').textContent=new Intl.DateTimeFormat('es-AR',{day:'2-digit',month:'short',year:'numeric'}).format(nextCheck).replace('.','');$('#pipelineCoverage').textContent=`${rows.length}/${zones.length} zonas`;
  $('#marketTable').innerHTML=`<div class="market-table-grid"><div class="market-table-head">Zona</div><div class="market-table-head">Depto. USD/m²</div><div class="market-table-head">Venta mediana</div><div class="market-table-head">Alquiler mediano</div><div class="market-table-head">Muestra</div>${rows.map(([id,row])=>`<div class="market-zone-cell"><span class="market-swatch" style="background:${marketColor(row.apartment_price_usd_m2)}"></span><b>${zones.find(z=>z.id===id).name}</b><small>${row.source_neighborhood}${row.match==='spelling_variant'?' · variante de nombre':''}</small></div><div><b>US$ ${fmt(Math.round(row.apartment_price_usd_m2))}</b></div><div>US$ ${fmt(Math.round(row.median_sale_usd))}</div><div>${row.median_rent_usd_month?`US$ ${fmt(Math.round(row.median_rent_usd_month))}`:'Sin muestra'}</div><div>${fmt(row.listings_total)} avisos</div>`).join('')}</div>`;
  if(affordabilityData)renderAffordabilityCalculator();
}

async function loadAffordabilityData(){
  try{
    let response;
    try{response=await fetch(`${AFFORDABILITY_REMOTE_URL}?v=${Date.now()}`,{cache:'no-store'});if(!response.ok)throw new Error(`HTTP ${response.status}`);affordabilityData=await response.json();if(affordabilityData?.schema_version!=='1.0')throw new Error('Datos remotos inválidos')}
    catch(remoteError){response=await fetch('data/affordability-santa-fe.json');if(!response.ok)throw new Error(`HTTP ${response.status}`);affordabilityData=await response.json();if(affordabilityData?.schema_version!=='1.0')throw new Error('Datos locales inválidos')}
    renderAffordability();
  }catch(error){console.error('No se pudieron cargar los datos de accesibilidad',error);$('#affIncome').textContent='No disponible';$('#affUpdated').textContent='No fue posible cargar la serie oficial.'}
}

function renderIncomeChart(rows){
  const target=$('#incomeChart'),values=rows.map(row=>row.median_household_income_ars_month),max=Math.max(...values)*1.18,barWidth=650/rows.length;
  const guides=[0,.5,1].map(f=>{const gy=45+f*165,value=max-f*max;return `<line x1="42" y1="${gy}" x2="692" y2="${gy}" class="data-gridline"/><text x="36" y="${gy+4}" text-anchor="end" class="data-axis">${(value/1000000).toFixed(1).replace('.',',')}M</text>`}).join('');
  const bars=values.map((value,index)=>{const height=value/max*165;return `<rect x="${48+index*barWidth}" y="${210-height}" width="${Math.max(26,barWidth-20)}" height="${height}" rx="7" class="income-bar${index===values.length-1?' latest':''}"><title>${quarterLabel(rows[index].period)}: ${money(value)}</title></rect><text x="${48+index*barWidth+Math.max(26,barWidth-20)/2}" y="${202-height}" text-anchor="middle" class="data-value">${(value/1000000).toFixed(2).replace('.',',')}M</text>`}).join('');
  target.innerHTML=`${guides}${bars}`;
}

function affordabilityPricePerM2(){
  if(!marketData)return null;
  const selected=$('#affZone').value;
  if(selected==='city')return marketData.city.median_apartment_price_usd_m2;
  return marketData.zones?.[selected]?.apartment_price_usd_m2??null;
}

function renderAffordabilityCalculator(){
  if(!affordabilityData||!marketData)return;
  const priceM2=affordabilityPricePerM2(),area=Math.max(20,Math.min(300,Number($('#affArea').value)||50)),down=Math.max(0,Math.min(90,Number($('#affDownPayment').value)||0));
  if(!priceM2)return;
  const propertyPrice=priceM2*area,initialCapital=propertyPrice*down/100,incomeUsd=affordabilityData.income.median_household_income_ars_month/affordabilityData.exchange_rate.ars_per_usd;
  const months=initialCapital/incomeUsd,years=propertyPrice/(incomeUsd*12);
  $('#affPropertyPrice').textContent=`US$ ${fmt(Math.round(propertyPrice))}`;$('#affInitialCapital').textContent=`US$ ${fmt(Math.round(initialCapital))}`;$('#affIncomeMonths').textContent=`${months.toFixed(1).replace('.',',')} meses`;$('#affIncomeYears').textContent=`${years.toFixed(1).replace('.',',')} años`;
  $('#affCalculationNote').textContent=`${fmt(area)} m² × US$ ${fmt(Math.round(priceM2))}/m² · ingreso convertido a US$ ${fmt(Math.round(incomeUsd))}/mes con dólar BCRA vendedor.`;
}

function renderAffordability(){
  const {income,credit,exchange_rate:fx,calculator}=affordabilityData;
  $('#affIncome').textContent=money(income.median_household_income_ars_month);$('#affIncomePeriod').textContent=`Gran Santa Fe · ${quarterLabel(income.latest_period)}`;$('#affRate').textContent=`UVA + ${credit.mortgage_uva_nominal_annual_rate_pct.toFixed(2).replace('.',',')}%`;$('#affCreditPeriod').textContent=`promedio del sistema · ${periodLabel(credit.latest_period)}`;$('#affTerm').textContent=`${credit.mortgage_uva_average_term_years.toFixed(1).replace('.',',')} años`;$('#affUva').textContent=money(credit.uva_ars);$('#affUvaDate').textContent=`BCRA · ${credit.uva_date.split('-').reverse().join('/')}`;
  $('#affCreditAmount').textContent=`${money(credit.mortgage_uva_amount_granted_ars/1000000000)} mil millones`;$('#affRateExplain').textContent=`UVA + ${credit.mortgage_uva_nominal_annual_rate_pct.toFixed(2).replace('.',',')}% no es una tasa fija en pesos.`;$('#affLimitations').textContent=calculator.limitations;$('#affUpdated').textContent=`EPH ${quarterLabel(income.latest_period)} · crédito ${periodLabel(credit.latest_period)} · dólar BCRA ${fx.date.split('-').reverse().join('/')}`;
  renderIncomeChart(income.series);renderAffordabilityCalculator();
}

function pipelinePeriod(value){
  if(!value)return 'Sin datos';
  if(value.includes('-Q'))return quarterLabel(value);
  if(value.length===10)return value.split('-').reverse().join('/');
  return periodLabel(value);
}

async function loadPipelineStatus(){
  try{
    let response;
    try{response=await fetch(`${PIPELINE_REMOTE_URL}?v=${Date.now()}`,{cache:'no-store'});if(!response.ok)throw new Error(`HTTP ${response.status}`);pipelineData=await response.json()}
    catch(remoteError){response=await fetch('data/pipeline-status.json');if(!response.ok)throw new Error(`HTTP ${response.status}`);pipelineData=await response.json()}
    if(pipelineData?.schema_version!=='1.0'||!pipelineData?.connectors)throw new Error('Estado inválido');
    renderPipelineStatus();
  }catch(error){console.error('No se pudo cargar el estado de conectores',error);$('#officialPipelineTitle').textContent='Estado no disponible';$('#officialPipelineChecked').textContent='Los datos publicados continúan visibles';$('#officialPipelineDot').classList.add('error')}
}

function renderPipelineStatus(){
  const healthy=pipelineData.status==='healthy',setup=pipelineData.status==='setup_required',checked=new Date(pipelineData.checked_at);
  $('#officialPipelineTitle').textContent=healthy?'Todos los conectores respondieron':setup?'Mercado Libre requiere OAuth':'Actualización parcial · datos protegidos';$('#officialPipelineChecked').textContent=`Último control: ${new Intl.DateTimeFormat('es-AR',{dateStyle:'medium',timeStyle:'short',timeZone:'America/Argentina/Cordoba'}).format(checked)} · próximo: día 1`;$('#officialPipelineDot').classList.toggle('error',!healthy&&!setup);$('#officialPipelineDot').classList.toggle('pending',setup);
  $('#officialConnectorGrid').innerHTML=Object.values(pipelineData.connectors).map(connector=>`<article class="connector-card ${connector.status}"><div><span class="connector-state"><i></i>${connector.status==='active'?'Activo':connector.status==='pending'?'Pendiente':'Revisar'}</span><small>${connector.cadence}</small></div><b>${connector.label}</b><span>${connector.publisher}</span><strong>${pipelinePeriod(connector.latest_period)}</strong><p>${connector.detail}</p></article>`).join('');
  const market=pipelineData.connectors.tulugar;if(market){$('#pipelineStatus').textContent=market.status==='active'?'Automatización activa':'Último dato válido conservado';}
}

function renderLineChart(target,rows,key){
  const values=rows.map(row=>row[key]),min=Math.min(...values)*.96,max=Math.max(...values)*1.03,x=index=>42+index*(650/(rows.length-1)),y=value=>210-(value-min)/(max-min)*165;
  const points=values.map((value,index)=>`${x(index)},${y(value)}`).join(' ');
  const guides=[0,.5,1].map(f=>{const gy=45+f*165,value=max-f*(max-min);return `<line x1="42" y1="${gy}" x2="692" y2="${gy}" class="data-gridline"/><text x="36" y="${gy+4}" text-anchor="end" class="data-axis">${Math.round(value/1000)}k</text>`}).join('');
  target.innerHTML=`${guides}<path d="M ${points} L ${x(rows.length-1)} 210 L 42 210 Z" class="data-area"/><polyline points="${points}" class="data-line"/><circle cx="${x(rows.length-1)}" cy="${y(values.at(-1))}" r="5" class="data-dot"/><text x="${x(rows.length-1)-6}" y="${y(values.at(-1))-12}" text-anchor="end" class="data-value">${money(values.at(-1))}</text>`;
}

function renderBarChart(target,rows,key){
  const values=rows.map(row=>row[key]),max=Math.max(...values)*1.15,barWidth=650/rows.length;
  const guides=[0,.5,1].map(f=>{const gy=45+f*165,value=max-f*max;return `<line x1="42" y1="${gy}" x2="692" y2="${gy}" class="data-gridline"/><text x="36" y="${gy+4}" text-anchor="end" class="data-axis">${Math.round(value/1000)}k</text>`}).join('');
  const bars=values.map((value,index)=>{const height=value/max*165;return `<rect x="${44+index*barWidth}" y="${210-height}" width="${Math.max(7,barWidth-7)}" height="${height}" rx="4" class="data-bar${index===values.length-1?' latest':''}"><title>${periodLabel(rows[index].period)}: ${fmt(value)} m²</title></rect>`}).join('');
  target.innerHTML=`${guides}${bars}<text x="688" y="32" text-anchor="end" class="data-value">${fmt(values.at(-1))} m²</text>`;
}

function renderConstruction(){
  const data=constructionData,summary=data.summary,costs=data.cost_gran_santa_fe,permits=data.permits_santa_fe_city;
  $('#constructionCost').textContent=money(summary.cost_ars_m2);$('#constructionMonthly').textContent=pct(summary.cost_monthly_change_pct);$('#constructionPeriod').textContent=`${periodLabel(data.latest_period)} · dato provisorio`;
  $('#permitsYtd').textContent=`${fmt(summary.permits_ytd_m2)} m²`;$('#permitsChange').textContent=pct(summary.permits_ytd_change_pct);$('#permitsChange').classList.toggle('negative',summary.permits_ytd_change_pct<0);
  $('#constructionUpdated').textContent=`Fuente actualizada a ${periodLabel(data.latest_period)} · descarga ${data.generated_at}`;
  renderLineChart($('#costChart'),costs,'total_ars_m2');renderBarChart($('#permitsChart'),permits,'authorized_m2');
  $('#costChartStart').textContent=periodLabel(costs[0].period);$('#costChartEnd').textContent=periodLabel(costs.at(-1).period);$('#permitsChartStart').textContent=periodLabel(permits[0].period);$('#permitsChartEnd').textContent=periodLabel(permits.at(-1).period);
}
function calcScore(z,profile=state.strategy){const p=profiles[profile];const yieldScore=Math.min(100,z.yield*12);const growthScore=Math.min(100,Math.max(0,z.growth*9));return Math.round(z.demand*p.demand+z.development*p.development+z.infrastructure*p.infrastructure+yieldScore*p.yield+growthScore*p.growth-z.risk*p.risk)}
function metricValue(z){if(state.metric==='market')return marketForZone(z)?.apartment_price_usd_m2??null;if(state.metric==='score')return calcScore(z);if(state.metric==='yield')return z.yield*12;if(state.metric==='growth')return z.growth*9;if(state.metric==='development')return z.development;if(state.metric==='risk')return 100-z.risk;return z.base}
function colorFor(v){return v>=80?'#239669':v>=65?'#53b889':v>=45?'#e6b94c':v>=25?'#e88935':'#cf5454'}
function metricDisplay(z){if(state.metric==='market'){const value=metricValue(z);return value==null?'S/D':value>=1000?`${(value/1000).toFixed(1)}k`:Math.round(value)}if(state.metric==='yield')return z.yield.toFixed(1).replace('.',',')+'%';if(state.metric==='growth')return '+'+z.growth.toFixed(1).replace('.',',')+'%';if(state.metric==='risk')return z.risk;return Math.round(metricValue(z))}
function isCensusMetric(){return state.metric==='population'||state.metric==='renters'}
function censusColor(value){
  if(state.metric==='renters')return value>=35?'#175f4a':value>=27?'#239669':value>=20?'#53b889':value>=12?'#e6b94c':'#cf5454';
  return value>=1200?'#175f4a':value>=900?'#239669':value>=600?'#53b889':value>=300?'#e6b94c':'#cf5454';
}
function censusStyle(feature){const p=feature.properties;const value=state.metric==='renters'?p.rented_pct:p.population;return{color:'#ffffff',weight:.65,fillColor:censusColor(value),fillOpacity:.72}}
function censusPopup(p){return `<div class="census-popup"><span>INDEC · Censo 2022</span><b>Radio ${p.radio}</b><dl><div><dt>Población*</dt><dd>${fmt(p.population)}</dd></div><div><dt>Hogares</dt><dd>${fmt(p.households)}</dd></div><div><dt>Viviendas</dt><dd>${fmt(p.dwellings)}</dd></div><div><dt>Hogares inquilinos</dt><dd>${p.rented_pct.toFixed(1).replace('.',',')}%</dd></div></dl><small>*En viviendas particulares</small></div>`}
async function loadCensusData(){
  try{
    const response=await fetch('data/censo-2022-santa-fe-radios.geojson');
    if(!response.ok)throw new Error('No se pudo cargar la capa censal');
    censusData=await response.json();
    censusLayer=L.geoJSON(censusData,{style:censusStyle,onEachFeature:(feature,layer)=>{layer.bindTooltip(`Radio ${feature.properties.radio}`,{sticky:true,className:'zone-tooltip'});layer.bindPopup(censusPopup(feature.properties),{maxWidth:280})}});
    const t=censusData.totals;$('#cityPopulation').textContent=fmt(t.population_private_dwellings);$('#cityHouseholds').textContent=fmt(t.households);$('#cityRenters').textContent=t.rented_pct.toFixed(1).replace('.',',')+'%';
    updateZoneCensus(zones.find(z=>z.id===state.selected));
    applyMapMode();
  }catch(error){
    $('#censusRadio').textContent='La capa censal no está disponible en este momento.';
    $$('.census-layer').forEach(button=>button.disabled=true);
  }
}
function pointInRing(point,ring){let inside=false;const x=point[0],y=point[1];for(let i=0,j=ring.length-1;i<ring.length;j=i++){const xi=ring[i][0],yi=ring[i][1],xj=ring[j][0],yj=ring[j][1];const crosses=((yi>y)!==(yj>y))&&(x<(xj-xi)*(y-yi)/(yj-yi)+xi);if(crosses)inside=!inside}return inside}
function pointInPolygon(point,polygon){if(!pointInRing(point,polygon[0]))return false;return !polygon.slice(1).some(ring=>pointInRing(point,ring))}
function featureContains(feature,lng,lat){const g=feature.geometry;if(g.type==='Polygon')return pointInPolygon([lng,lat],g.coordinates);if(g.type==='MultiPolygon')return g.coordinates.some(polygon=>pointInPolygon([lng,lat],polygon));return false}
function censusForZone(z){return censusData?.features.find(feature=>featureContains(feature,z.lng,z.lat))}
function updateZoneCensus(z){
  if(!censusData){$('#censusRadio').textContent='Cargando radio censal…';return}
  const feature=censusForZone(z);
  if(!feature){$('#censusRadio').textContent='El punto de referencia no coincide con un radio disponible.';['#censusPopulation','#censusHouseholds','#censusDwellings','#censusRenters'].forEach(id=>$(id).textContent='—');return}
  const p=feature.properties;$('#censusRadio').textContent=`Radio ${p.radio} · punto ubicado dentro de este radio`;$('#censusPopulation').textContent=fmt(p.population);$('#censusHouseholds').textContent=fmt(p.households);$('#censusDwellings').textContent=fmt(p.dwellings);$('#censusRenters').textContent=`${fmt(p.rented_households)} · ${p.rented_pct.toFixed(1).replace('.',',')}%`;
}
function updateLegend(){
  const title=$('.legend-title span'),labels=$('.legend-labels');
  if(state.metric==='population'){title.textContent='Población por radio';labels.innerHTML='<span>&lt; 300</span><span>600—899</span><span>≥ 1.200</span>';return}
  if(state.metric==='renters'){title.textContent='Hogares inquilinos';labels.innerHTML='<span>&lt; 12%</span><span>20—26%</span><span>≥ 35%</span>';return}
  if(state.metric==='market'){title.textContent='Deptos. USD/m²';labels.innerHTML='<span>Sin dato / bajo</span><span>US$ 1.400</span><span>≥ US$ 2.000</span>';return}
  const active=$(`.layer-button[data-metric="${state.metric}"]`);title.textContent=active?active.textContent.trim():'Potencial';labels.innerHTML='<span>Muy bajo</span><span>Moderado</span><span>Muy alto</span>';
}
function applyMapMode(){
  if(isCensusMetric()){
    markers.forEach(marker=>{if(map.hasLayer(marker))map.removeLayer(marker)});
    if(censusLayer){if(!map.hasLayer(censusLayer))censusLayer.addTo(map);censusLayer.setStyle(censusStyle);$('#visibleStat').innerHTML=`<b>${censusData.features.length}</b><span>radios censales</span>`}
    $('#mapSourceLink').href='https://redatam.indec.gob.ar/binarg/RpWebEngine.exe/Portal?BASE=CPV2022&lang=ESP';$('#mapSourceLink').textContent='Datos oficiales · INDEC ↗';
  }else{
    if(censusLayer&&map.hasLayer(censusLayer))map.removeLayer(censusLayer);
    renderMarkers();
    if(state.metric==='market'){$('#mapSourceLink').href='https://tulugar.com/es/datos';$('#mapSourceLink').textContent='Precios de oferta · TuLugar ↗'}else{$('#mapSourceLink').href='https://www.santafe.gob.ar/idesf/geoportal/paginas/servicios-OGC';$('#mapSourceLink').textContent='Límites oficiales · SCIT/IDESF ↗'}
  }
  updateLegend();
}

function initMap(){
  map=L.map('map',{zoomControl:false,attributionControl:true}).setView([-31.637,-60.696],13);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:18,attribution:'&copy; OpenStreetMap'}).addTo(map);
  officialBoundaries=L.tileLayer.wms('https://aswe.santafe.gov.ar/idesf/wms',{
    layers:'scit_vecinales',format:'image/png',transparent:true,version:'1.1.1',
    attribution:'Límites vecinales: SCIT / IDESF',opacity:.72
  }).addTo(map);
  L.control.zoom({position:'bottomright'}).addTo(map);renderMarkers();loadCensusData();
}
function renderMarkers(){if(isCensusMetric())return;let visible=0;zones.forEach(z=>{const score=calcScore(z),market=marketForZone(z),show=state.metric==='market'||score>=state.minScore;if(show&&(state.metric!=='market'||market))visible++;const val=metricValue(z),color=state.metric==='market'?marketColor(val):colorFor(val);const html=`<div class="zone-marker ${z.id===state.selected?'selected':''} ${state.metric==='market'&&!market?'no-data':''}" style="background:${color}">${metricDisplay(z)}</div>`;if(!markers.has(z.id)){const marker=L.marker([z.lat,z.lng],{icon:L.divIcon({className:'',html,iconSize:[40,40],iconAnchor:[20,20]}),zIndexOffset:z.id===state.selected?500:0}).addTo(map);marker.bindTooltip(z.name,{direction:'top',offset:[0,-19],className:'zone-tooltip'});marker.on('click',()=>selectZone(z.id,true));markers.set(z.id,marker)}else{const marker=markers.get(z.id);marker.setIcon(L.divIcon({className:'',html,iconSize:[40,40],iconAnchor:[20,20]}));marker.setZIndexOffset(z.id===state.selected?500:0)}const marker=markers.get(z.id);if(show&&!map.hasLayer(marker))marker.addTo(map);if(!show&&map.hasLayer(marker))map.removeLayer(marker)});$('#visibleStat').innerHTML=`<b>${visible}</b><span>${state.metric==='market'?'zonas con precio real':'zonas con indicador'}</span>`}
function selectZone(id,open=false){state.selected=id;const z=zones.find(x=>x.id===id);const score=calcScore(z);$('#zoneName').textContent=z.name;$('#zoneType').textContent=z.type;$('#zoneScore').textContent=score;$('#scoreRing').style.background=`conic-gradient(${colorFor(score)} 0 ${score}%,#e4ece8 ${score}%)`;$('#scoreLabel').textContent=score>=80?'Potencial muy alto':score>=65?'Potencial alto':score>=45?'Potencial moderado':'Potencial limitado';$('#scoreLabel').style.color=colorFor(score);$('#confidenceText').textContent=`Confianza ${z.observations>=80?'alta':z.observations>=40?'media':'baja'} · ${z.observations} observaciones`;$('#trendText').innerHTML=`<b>Tendencia ${z.delta>2?'positiva':z.delta<0?'negativa':'estable'}</b><br />${z.delta>=0?'Mejoró':'Retrocedió'} ${Math.abs(z.delta)} puntos en los últimos 12 meses`;$('#priceMetric').textContent=`US$ ${fmt(z.price)}`;$('#yieldMetric').textContent=z.yield.toFixed(1).replace('.',',')+'%';$('#growthMetric').textContent=(z.growth>=0?'+':'')+z.growth.toFixed(1).replace('.',',')+'%';$('#devMetric').textContent=z.development;$('#chartDelta').textContent=(z.delta>=0?'+':'')+z.delta;$('#chartDelta').className=z.delta>=0?'positive':'';renderChart(z);renderDrivers(z);updateZoneCensus(z);updateZoneMarket(z);renderMarkers();if(open){$('#insightPanel').classList.remove('closed');if(innerWidth<=850)map.panTo([z.lat,z.lng])}}
function renderChart(z){const values=z.history,min=Math.min(...values)-2,max=Math.max(...values)+2,pts=values.map((v,i)=>`${i*(350/(values.length-1))+5},${90-(v-min)/(max-min)*72}`).join(' ');const end=pts.split(' ').at(-1).split(',');$('#scoreChart').innerHTML=`<defs><linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#53b889" stop-opacity=".28"/><stop offset="100%" stop-color="#53b889" stop-opacity="0"/></linearGradient></defs><path d="M ${pts} L 355 96 L 5 96 Z" class="chart-area"/><polyline points="${pts}" class="chart-line"/><circle cx="${end[0]}" cy="${end[1]}" r="4" class="chart-dot"/>`}
function renderDrivers(z){$('#driversList').innerHTML=z.drivers.map(([label,val])=>`<div class="driver-row"><span>${label}</span><span class="impact-bar"><i style="width:${val}%"></i></span><b>${val}</b></div>`).join('')}
function bestZone(){const visible=zones.filter(z=>calcScore(z)>=state.minScore).sort((a,b)=>calcScore(b)-calcScore(a))[0];if(!visible)return;selectZone(visible.id,true);map.flyTo([visible.lat,visible.lng],14,{duration:.7})}

function renderRanking(profile=state.strategy){const sorted=[...zones].sort((a,b)=>calcScore(b,profile)-calcScore(a,profile));$('#rankingList').innerHTML=sorted.map((z,i)=>`<article class="ranking-card"><span class="rank-number">${String(i+1).padStart(2,'0')}</span><div class="rank-zone"><b>${z.name}</b><small>${z.type.split(' · ')[0]} · ${z.observations} observaciones</small></div><div class="rank-metric"><small>Precio / m²</small><b>US$ ${fmt(z.price)}</b></div><div class="rank-metric"><small>Renta bruta</small><b>${z.yield.toFixed(1).replace('.',',')}%</b></div><div class="rank-metric optional"><small>Valorización</small><b>+${z.growth.toFixed(1).replace('.',',')}%</b></div><div class="rank-metric optional"><small>Riesgo</small><b>${z.risk}/100</b></div><div><span class="rank-score">${calcScore(z,profile)}</span><button class="add-compare ${state.compare.includes(z.id)?'active':''}" data-compare="${z.id}">${state.compare.includes(z.id)?'Agregada':'+ Comparar'}</button></div></article>`).join('');$$('[data-compare]').forEach(b=>b.addEventListener('click',()=>toggleCompare(b.dataset.compare)))}
function toggleCompare(id){if(state.compare.includes(id))state.compare=state.compare.filter(x=>x!==id);else if(state.compare.length<3)state.compare.push(id);renderRanking($('#rankingStrategy').value);renderCompareSelection()}
function renderCompareSelection(){const box=$('#compareSelection');box.innerHTML=state.compare.length?state.compare.map(id=>{const z=zones.find(x=>x.id===id);return `<div class="compare-chip"><span>${z.name}</span><button data-remove="${id}" aria-label="Quitar ${z.name}">×</button></div>`}).join(''):'<div class="empty-selection">Todavía no seleccionaste zonas</div>';$$('[data-remove]').forEach(b=>b.addEventListener('click',()=>toggleCompare(b.dataset.remove)));$('#runComparison').disabled=state.compare.length<2}
function renderComparison(){const selected=state.compare.map(id=>zones.find(z=>z.id===id));const rows=[['Puntaje',z=>calcScore(z,$('#rankingStrategy').value)],['Precio mediano',z=>'US$ '+fmt(z.price)+' /m²'],['Renta bruta',z=>z.yield.toFixed(1).replace('.',',')+'%'],['Valorización',z=>'+'+z.growth.toFixed(1).replace('.',',')+'%'],['Desarrollo',z=>z.development+'/100'],['Demanda',z=>z.demand+'/100'],['Infraestructura',z=>z.infrastructure+'/100'],['Riesgo',z=>z.risk+'/100'],['Confianza',z=>z.observations>=80?'Alta':z.observations>=40?'Media':'Baja']];$('#comparisonTable').innerHTML=`<div class="compare-grid" style="--cols:${selected.length}"><div class="grid-head">Indicador</div>${selected.map(z=>`<div class="grid-head">${z.name}</div>`).join('')}${rows.map(([label,fn])=>`<div class="grid-label">${label}</div>${selected.map(z=>`<div><b>${fn(z)}</b></div>`).join('')}`).join('')}</div>`;$('#comparisonResult').hidden=false;$('#comparisonResult').scrollIntoView({behavior:'smooth'})}

function switchView(view){$$('.view').forEach(v=>v.classList.toggle('active',v.id===`view-${view}`));$$('.nav-link').forEach(b=>b.classList.toggle('active',b.dataset.view===view));if(view==='mapa')setTimeout(()=>map.invalidateSize(),50);if(view==='zonas'){renderRanking($('#rankingStrategy').value);renderCompareSelection()}}

document.addEventListener('DOMContentLoaded',()=>{
  initMap();loadConstructionData();loadMarketData();loadMeliData();loadAffordabilityData();loadPipelineStatus();selectZone(state.selected);
  $('#strategy').addEventListener('change',e=>{state.strategy=e.target.value;renderMarkers();selectZone(state.selected)});
  $('#minScore').addEventListener('input',e=>{state.minScore=+e.target.value;$('#scoreOutput').textContent=e.target.value;renderMarkers()});
  $$('.layer-button').forEach(b=>b.addEventListener('click',()=>{$$('.layer-button').forEach(x=>x.classList.remove('active'));b.classList.add('active');state.metric=b.dataset.metric;applyMapMode()}));
  $$('.nav-link').forEach(b=>b.addEventListener('click',()=>switchView(b.dataset.view)));
  ['#affZone','#affArea','#affDownPayment'].forEach(selector=>$(selector).addEventListener('input',renderAffordabilityCalculator));
  $('#bestZoneButton').addEventListener('click',bestZone);$('#closePanel').addEventListener('click',()=>$('#insightPanel').classList.add('closed'));
  $('#rankingStrategy').addEventListener('change',e=>renderRanking(e.target.value));$('#runComparison').addEventListener('click',renderComparison);$('#closeComparison').addEventListener('click',()=>$('#comparisonResult').hidden=true);
  $('#compareCurrent').addEventListener('click',()=>{if(!state.compare.includes(state.selected)&&state.compare.length<3)state.compare.push(state.selected);switchView('zonas')});
  const dialog=$('#infoDialog');$('#openInfo').addEventListener('click',()=>dialog.showModal());$('#legendHelp').addEventListener('click',()=>dialog.showModal());$('.dialog-close').addEventListener('click',()=>dialog.close());dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});
  if(innerWidth<=1150)$('#insightPanel').classList.add('closed');
});
