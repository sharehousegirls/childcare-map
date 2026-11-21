// DEMO ONLY: fictional sample records. Replace with verified public data before launch.
const demoRegions=[
 {name:"안성시",district:"경기도",facilities:42,waiting:318,zero:11,avg:7.6},
 {name:"대구 수성구",district:"대구광역시",facilities:56,waiting:426,zero:14,avg:8.1},
 {name:"대구 달서구",district:"대구광역시",facilities:63,waiting:504,zero:18,avg:8.0},
 {name:"수원시 영통구",district:"경기도",facilities:71,waiting:610,zero:16,avg:8.6},
 {name:"천안시 서북구",district:"충청남도",facilities:49,waiting:352,zero:13,avg:7.2},
 {name:"청주시 흥덕구",district:"충청북도",facilities:45,waiting:290,zero:15,avg:6.4}
];
const demoFacilities=[
 {name:"햇살 국공립 어린이집",region:"안성시",type:"국공립",address:"경기도 안성시 (예시 주소)",waiting:0,capacity:80,enrolled:72},
 {name:"푸른숲 어린이집",region:"안성시",type:"민간",address:"경기도 안성시 (예시 주소)",waiting:12,capacity:45,enrolled:43},
 {name:"별빛 어린이집",region:"대구 수성구",type:"가정",address:"대구 수성구 (예시 주소)",waiting:3,capacity:20,enrolled:18},
 {name:"꿈나무 직장 어린이집",region:"대구 수성구",type:"직장",address:"대구 수성구 (예시 주소)",waiting:0,capacity:60,enrolled:55},
 {name:"한마음 어린이집",region:"대구 달서구",type:"민간",address:"대구 달서구 (예시 주소)",waiting:17,capacity:55,enrolled:52},
 {name:"아이숲 어린이집",region:"대구 달서구",type:"국공립",address:"대구 달서구 (예시 주소)",waiting:6,capacity:70,enrolled:68},
 {name:"영통 행복 어린이집",region:"수원시 영통구",type:"국공립",address:"수원시 영통구 (예시 주소)",waiting:0,capacity:90,enrolled:84},
 {name:"새싹 어린이집",region:"천안시 서북구",type:"가정",address:"천안시 서북구 (예시 주소)",waiting:4,capacity:20,enrolled:19},
 {name:"청주 꿈 어린이집",region:"청주시 흥덕구",type:"민간",address:"청주시 흥덕구 (예시 주소)",waiting:9,capacity:50,enrolled:46}
];
const regionSelect=document.querySelector("#regionSelect");
const regionCards=document.querySelector("#regionCards");
const facilityList=document.querySelector("#facilityList");
demoRegions.forEach(r=>{const o=document.createElement("option");o.value=r.name;o.textContent=r.name;regionSelect.append(o)});
function selectedRegion(){return regionSelect.value}
function renderSummary(){const rs=selectedRegion()==="all"?demoRegions:demoRegions.filter(r=>r.name===selectedRegion());const fac=rs.reduce((s,r)=>s+r.facilities,0);const wait=rs.reduce((s,r)=>s+r.waiting,0);document.querySelector("#summaryStats").innerHTML=`<div class="stat"><span>시설 수 (예시)</span><strong>${fac.toLocaleString()}개</strong></div><div class="stat"><span>대기 인원 (예시)</span><strong>${wait.toLocaleString()}명</strong></div>`}
function renderRegions(){const rs=selectedRegion()==="all"?demoRegions:demoRegions.filter(r=>r.name===selectedRegion());const max=Math.max(...demoRegions.map(r=>r.avg));regionCards.innerHTML=rs.map(r=>`<article class="region-card"><h3>${r.name}</h3><p>${r.district} · 시설 ${r.facilities}개</p><div class="region-metrics"><div class="metric"><small>총 대기 (예시)</small><strong>${r.waiting.toLocaleString()}명</strong></div><div class="metric"><small>시설당 평균 (예시)</small><strong>${r.avg}명</strong></div><div class="metric"><small>대기 0명 시설 (예시)</small><strong>${r.zero}개</strong></div><div class="metric"><small>0명 시설 비율</small><strong>${Math.round(r.zero/r.facilities*100)}%</strong></div></div><div class="bar"><i style="width:${r.avg/max*100}%"></i></div></article>`).join("")}
function renderFacilities(){let rows=demoFacilities.filter(f=>selectedRegion()==="all"||f.region===selectedRegion());const q=document.querySelector("#facilitySearch").value.trim().toLowerCase();const type=document.querySelector("#typeFilter").value;const zero=document.querySelector("#zeroFilter").checked;if(q)rows=rows.filter(f=>f.name.toLowerCase().includes(q));if(type!=="all")rows=rows.filter(f=>f.type===type);if(zero)rows=rows.filter(f=>f.waiting===0);facilityList.innerHTML=rows.length?rows.map(f=>`<article class="facility-card"><div><h3>${f.name}</h3><p>${f.region} · ${f.type}<br>${f.address}<br>정원 ${f.capacity}명 · 현원 ${f.enrolled}명</p></div><span class="facility-badge ${f.waiting===0?"zero":""}">대기 ${f.waiting}명</span></article>`).join(""):'<div class="empty">조건에 맞는 시설이 없습니다.</div>'}
function render(){renderSummary();renderRegions();renderFacilities()}
regionSelect.addEventListener("change",render);document.querySelector("#facilitySearch").addEventListener("input",renderFacilities);document.querySelector("#typeFilter").addEventListener("change",renderFacilities);document.querySelector("#zeroFilter").addEventListener("change",renderFacilities);render();