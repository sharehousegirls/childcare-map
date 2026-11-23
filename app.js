import { readSavedSearches, saveSavedSearch, removeSavedSearch } from "./saved-searches.mjs";
import { groupRegionOptions } from "./region-selector.mjs";
import { readSavedRegions, saveSavedRegion, removeSavedRegion } from "./saved-regions.mjs";
import { buildRegions } from "./regional-summary.mjs";
import { readSavedFacilities, saveSavedFacility, removeSavedFacility } from "./saved-facilities.mjs";
import { formatDataQualityDetails } from "./data-quality.mjs";
import { formatDataFreshness } from "./data-freshness.mjs";

// Live backend is preferred when configured; otherwise clearly labeled fictional demo.
const DEMO_REGIONS=[
{name:"안성시",district:"경기도",facilities:42,waiting:318,zero:11,avg:7.6},
{name:"대구 수성구",district:"대구광역시",facilities:56,waiting:426,zero:14,avg:8.1},
{name:"대구 달서구",district:"대구광역시",facilities:63,waiting:504,zero:18,avg:8.0},
{name:"수원시 영통구",district:"경기도",facilities:71,waiting:610,zero:16,avg:8.6},
{name:"천안시 서북구",district:"충청남도",facilities:49,waiting:352,zero:13,avg:7.2},
{name:"청주시 흥덕구",district:"충청북도",facilities:45,waiting:290,zero:15,avg:6.4}];
const DEMO_FACILITIES=[
{facilityId:"demo-ansung-sunshine",name:"햇살 국공립 어린이집",region:"안성시",type:"국공립",address:"경기도 안성시 (예시 주소)",waiting:0,capacity:80,enrolled:72},
{facilityId:"demo-ansung-greenforest",name:"푸른숲 어린이집",region:"안성시",type:"민간",address:"경기도 안성시 (예시 주소)",waiting:12,capacity:45,enrolled:43},
{facilityId:"demo-suseong-starlight",name:"별빛 어린이집",region:"대구 수성구",type:"가정",address:"대구 수성구 (예시 주소)",waiting:3,capacity:20,enrolled:18},
{facilityId:"demo-suseong-dreamwork",name:"꿈나무 직장 어린이집",region:"대구 수성구",type:"직장",address:"대구 수성구 (예시 주소)",waiting:0,capacity:60,enrolled:55},
{facilityId:"demo-dalseo-hanmaum",name:"한마음 어린이집",region:"대구 달서구",type:"민간",address:"대구 달서구 (예시 주소)",waiting:17,capacity:55,enrolled:52},
{facilityId:"demo-dalseo-forest",name:"아이숲 어린이집",region:"대구 달서구",type:"국공립",address:"대구 달서구 (예시 주소)",waiting:6,capacity:70,enrolled:68},
{facilityId:"demo-yeongtong-happy",name:"영통 행복 어린이집",region:"수원시 영통구",type:"국공립",address:"수원시 영통구 (예시 주소)",waiting:0,capacity:90,enrolled:84},
{facilityId:"demo-cheonan-sprout",name:"새싹 어린이집",region:"천안시 서북구",type:"가정",address:"천안시 서북구 (예시 주소)",waiting:4,capacity:20,enrolled:19},
{facilityId:"demo-heungdeok-dream",name:"청주 꿈 어린이집",region:"청주시 흥덕구",type:"민간",address:"청주시 흥덕구 (예시 주소)",waiting:9,capacity:50,enrolled:46}];
let regions=DEMO_REGIONS,facilities=DEMO_FACILITIES,liveData=false,liveError="",liveMeta=null;
const regionSelect=document.querySelector("#regionSelect"),regionCards=document.querySelector("#regionCards"),facilityList=document.querySelector("#facilityList"),statusEl=document.querySelector("#dataStatus"),dataQualityDetails=document.querySelector("#dataQualityDetails");
const dataFreshnessDetails=document.querySelector("#dataFreshnessDetails");
const facilitySearch=document.querySelector("#facilitySearch"),typeFilter=document.querySelector("#typeFilter"),zeroFilter=document.querySelector("#zeroFilter");
const savedSearchForm=document.querySelector("#savedSearchForm"),savedSearchName=document.querySelector("#savedSearchName"),savedSearchStatus=document.querySelector("#savedSearchStatus"),savedSearchList=document.querySelector("#savedSearchList");
const saveRegionButton=document.querySelector("#saveRegionButton"),savedRegionStatus=document.querySelector("#savedRegionStatus"),savedRegionList=document.querySelector("#savedRegionList");
const savedFacilityStatus=document.querySelector("#savedFacilityStatus"),savedFacilityList=document.querySelector("#savedFacilityList");
let focusedFacilityId=null;
function num(v){if(v==null||v==="")return null;const n=Number(String(v).replace(/,/g,""));return Number.isFinite(n)?n:null;}
function escapeHtml(value){return String(value??"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#39;");}
function mapApiRows(rows){return rows.map(r=>{const ages=[r.wait_0,r.wait_1,r.wait_2,r.wait_3,r.wait_4,r.wait_5,r.wait_6_plus].map(num);let waiting=num(r.wait_total);if(waiting===null&&ages.every(v=>v!==null))waiting=ages.reduce((a,b)=>a+b,0);return{name:String(r.name||"이름 미확인 시설"),region:[r.sido,r.sigungu].filter(Boolean).map(String).join(" ")||"지역 미분류",sido:String(r.sido||""),type:String(r.type||"유형 미확인"),address:String(r.address||"주소 미확인"),waiting,capacity:num(r.capacity),enrolled:num(r.enrolled),facilityId:r.facility_id==null?null:String(r.facility_id).trim()||null,latitude:num(r.latitude),longitude:num(r.longitude),dataDate:r.data_date==null?"":String(r.data_date)};});}
function populateRegions(){
  regionSelect.replaceChildren();
  const all=document.createElement("option");
  all.value="all";
  all.textContent="전체 지역";
  regionSelect.append(all);
  groupRegionOptions(regions).forEach(group=>{
    const optgroup=document.createElement("optgroup");
    opt.label=group.parent;
    group.options.forEach(option=>{
      const o=document.createElement("option");
      o.value=option.value;
      o.textContent=option.label;
      optgroup.append(o);
    });
    regionSelect.append(optgroup);
  });
}
function selectedRegion(){return regionSelect.value;}
function renderSummary(){
  const rs=selectedRegion()==="all"?regions:regions.filter(r=>r.name===selectedRegion());
  const fac=rs.reduce((s,r)=>s+r.facilities,0);
  const known=rs.reduce((s,r)=>s+(r.waitingFacilities||0),0);
  const missing=fac-known;
  const wait=known?rs.reduce((s,r)=>s+(r.waiting??0),0):null;
  const demoWait=rs.reduce((s,r)=>s+(r.waiting||0),0);
  const stats=document.querySelector("#summaryStats");
  stats.innerHTML=liveData
    ? '<div class="stat"><span>시설 수</span><strong>'+fac.toLocaleString()+'개</strong></div><div class="stat"><span>확인된 대기 합계</span><strong>'+(wait===null?"—":wait.toLocaleString())+'건</strong><small>대기 확인 시설 '+known.toLocaleString()+' / '+fac.toLocaleString()+'개 · 미확인 '+missing.toLocaleString()+'개</small></div>'
    : '<div class="stat"><span>시설 수 (예시)</span><strong>'+fac.toLocaleString()+'개</strong></div><div class="stat"><span>대기 인원 (예시)</span><strong>'+demoWait.toLocaleString()+'명</strong></div>';
}
function renderRegions(){
  const rs=selectedRegion()==="all"?regions:regions.filter(r=>r.name===selectedRegion());
  const max=Math.max(1,...regions.map(r=>r.avg||0));
  regionCards.innerHTML=rs.map(r=>{
    const waiting=r.waiting===null?"—":r.waiting.toLocaleString();
    const avg=r.avg==null?"—":r.avg.toFixed(1);
    const known=liveData?(r.waitingFacilities||0):r.facilities;
    const missing=liveData?(r.missingWaitlistFacilities||0):0;
    const zeroRate=liveData
      ? (r.zeroWaitRate==null?"—":Math.round(r.zeroWaitRate*100)+"%")
      : (known?Math.round((r.zero||0)/known*100)+"%":"—");
    return '<article class="region-card"><h3>'+escapeHtml(r.name)+'</h3><p>'+escapeHtml(r.district||"지역")+' · 시설 '+r.facilities+'개'+(liveData?'':' (예시)')+'</p><div class="region-metrics">'
      +'<div class="metric"><small>'+(liveData?'확인된 대기 합계':'총 대기 (예시)')+'</small><strong>'+waiting+(liveData?'건':'명')+'</strong></div>'
      +'<div class="metric"><small>'+(liveData?'대기 확인 시설당 평균':'시설당 평균 (예시)')+'</small><strong>'+avg+'건</strong></div>'
      +'<div class="metric"><small>'+(liveData?'대기 0건 시설':'대기 0명 시설 (예시)')+'</small><strong>'+(r.zero||0)+'개</strong></div>'
      +'<div class="metric"><small>'+(liveData?'0건 비율 (확인 시설 기준)':'0명 비율 (예시)')+'</small><strong>'+zeroRate+'</strong></div>'
      +'<div class="metric"><small>'+(liveData?'대기 정보 미확인 시설':'대기 정보 미확인 (예시)')+'</small><strong>'+missing+'개</strong></div>'
      +'</div><div class="bar"><i style="width:'+Math.min(100,(r.avg||0)/max*100)+'%"></i></div></article>';
  }).join("");
}
function renderFacilities(){
  let rows=facilities.filter(f=>selectedRegion()==="all"||f.region===selectedRegion());
  const q=facilitySearch.value.trim().toLowerCase(),type=typeFilter.value,zero=zeroFilter.checked;
  if(focusedFacilityId)rows=rows.filter(f=>String(f.facilityId||"")===focusedFacilityId);
  if(q)rows=rows.filter(f=>String(f.name||"").toLowerCase().includes(q));
  if(type!=="all")rows=rows.filter(f=>f.type===type);
  if(zero)rows=rows.filter(f=>f.waiting===0);
  facilityList.replaceChildren();
  if(!rows.length){const empty=document.createElement("div");empty.className="empty";empty.textContent="조건에 맞는 시설이 없습니다.";facilityList.append(empty);return;}
  const saved=readSavedFacilities();
  rows.forEach(f=>{
    const card=document.createElement("article");card.className="facility-card";
    if(f.facilityId)card.dataset.facilityId=String(f.facilityId);
    const details=document.createElement("div");details.className="facility-details";
    const heading=document.createElement("h3");heading.textContent=f.name||"이름 미확인 시설";
    const lines=[String(f.region||"지역 미확인")+" · "+String(f.type||"유형 미확인"),String(f.address||"주소 미확인")];
    if(f.capacity!=null)lines.push("정원 "+Number(f.capacity).toLocaleString()+"명");
    if(f.enrolled!=null)lines.push("현원 "+Number(f.enrolled).toLocaleString()+"명");
    const info=document.createElement("p");info.textContent=lines.join("\n");details.append(heading,info);
    const badge=document.createElement("span");badge.className="facility-badge"+(f.waiting===0?" zero":"");
    badge.textContent=f.waiting==null?"대기 확인 불가":(liveData?"대기 "+Number(f.waiting).toLocaleString()+"건":"대기 "+Number(f.waiting).toLocaleString()+"명 (예시)");
    const save=document.createElement("button");save.type="button";save.className="saved-facility-save";
    const facilityId=typeof f.facilityId==="string"?f.facilityId.trim():"";
    const isSaved=facilityId&&saved.some(item=>item.facilityId===facilityId);
    save.textContent=isSaved?"저장됨":"관심 시설 저장";save.disabled=!facilityId||Boolean(isSaved);
    save.setAttribute("aria-label",isSaved?heading.textContent+" 관심 시설 저장됨":heading.textContent+" 관심 시설 저장");
    if(facilityId)save.dataset.saveFacility=facilityId;else save.title="시설 고유 ID가 없어 저장할 수 없습니다.";
    card.append(details,badge,save);facilityList.append(card);
  });
}function render(){
 const dates=liveMeta?.source_data_dates?.length?liveMeta.source_data_dates:[...new Set(facilities.map(f=>f.dataDate).filter(Boolean))];
 const sourceDate=liveMeta?.source_data_date||(dates.length===1?dates[0]:null);
 const dateLabel=sourceDate?"기준일 "+sourceDate:dates.length>1?"시설별 기준일 혼재":"기준일 미확인";
 const collectedAt=liveMeta?.collected_at?new Date(liveMeta.collected_at):null;
 const collectionLabel=collectedAt&&!Number.isNaN(collectedAt.getTime())?" · 수집(현지) "+collectedAt.toLocaleString("ko-KR"):"";
 statusEl.textContent=liveData?"실제 API 데이터 연결 · "+dateLabel+collectionLabel:"가상 데모 데이터 · 실제 현황 아님";
 statusEl.className="data-status "+(liveData?"live":"demo");
 if(liveData){
   statusEl.title=liveMeta?.collected_at?"API 수집 시각(UTC): "+liveMeta.collected_at:"";
   dataQualityDetails.textContent=formatDataQualityDetails(liveMeta,facilities.length);
   dataFreshnessDetails.textContent=formatDataFreshness(liveMeta);
 }else{
   statusEl.title=liveError&&!liveData?"Backend 연결 오류: "+liveError:"";
   dataQualityDetails.textContent="가상 데모에는 실제 기준일 품질 진단이 없습니다.";
   dataFreshnessDetails.textContent="가상 데모에는 실제 데이터 최신성 정보가 없습니다.";
 }
 renderSummary();renderRegions();renderFacilities();
}
async function tryLoadLive(){try{const res=await fetch("http://127.0.0.1:8000/api/facilities");if(!res.ok)throw Error("Backend HTTP "+res.status);const data=await res.json();if(data.source!=="official_api"||!Array.isArray(data.facilities))throw Error("Unexpected API payload");if(!Number.isInteger(data.count)||data.count!==data.facilities.length)throw Error("API record count does not match facilities");const mapped=mapApiRows(data.facilities);if(!mapped.length)throw Error("No usable facility records");facilities=mapped;regions=buildRegions(mapped);liveMeta=data.meta&&typeof data.meta==="object"?data.meta:null;liveData=true;liveError="";}catch(e){liveData=false;liveError=e.message||String(e);liveMeta=null;facilities=DEMO_FACILITIES;regions=DEMO_REGIONS;}populateRegions();render();}
function showSavedSearchStatus(message,isError=false){savedSearchStatus.textContent=message;savedSearchStatus.className="saved-search-status"+(isError?" error":"");}
function savedSearchDescription(item){return [item.region==="all"?"전체 지역":item.region,item.query||"시설명 전체",item.type==="all"?"전체 유형":item.type,item.zeroWait?"대기 0명":"전체 대기"].join(" · ");}
function createSavedSearchId(){try{if(typeof crypto!=="undefined"&&crypto.randomUUID)return crypto.randomUUID();}catch{}return Date.now()+"-"+Math.random().toString(36).slice(2,10);}
function renderSavedSearches(){savedSearchList.replaceChildren();const items=readSavedSearches();if(!items.length){const empty=document.createElement("p");empty.className="saved-search-empty";empty.textContent="저장된 검색 조건이 없습니다.";savedSearchList.append(empty);return;}items.forEach(item=>{const row=document.createElement("article");row.className="saved-search-item";const info=document.createElement("div");info.className="saved-search-info";const name=document.createElement("strong");name.textContent=item.name;const meta=document.createElement("small");meta.textContent=savedSearchDescription(item);info.append(name,meta);const actions=document.createElement("div");actions.className="saved-search-actions";const load=document.createElement("button");load.type="button";load.className="saved-search-load";load.textContent="불러오기";load.dataset.loadSavedSearch=item.id;load.setAttribute("aria-label",item.name+" 검색 조건 불러오기");const remove=document.createElement("button");remove.type="button";remove.className="saved-search-delete";remove.textContent="삭제";remove.dataset.deleteSavedSearch=item.id;remove.setAttribute("aria-label",item.name+" 검색 조건 삭제");actions.append(load,remove);row.append(info,actions);savedSearchList.append(row);});}
function applySavedSearch(item){const regionExists=[...regionSelect.options].some(option=>option.value===item.region);regionSelect.value=regionExists?item.region:"all";facilitySearch.value=item.query;typeFilter.value=[...typeFilter.options].some(option=>option.value===item.type)?item.type:"all";zeroFilter.checked=item.zeroWait;render();showSavedSearchStatus(regionExists?"저장된 검색 조건을 적용했습니다.":"저장된 지역을 찾을 수 없어 전체 지역으로 적용했습니다.",!regionExists);}
savedSearchForm.addEventListener("submit",event=>{event.preventDefault();const region=selectedRegion(),query=facilitySearch.value.trim(),type=typeFilter.value,zeroWait=zeroFilter.checked;const generatedName=[region==="all"?"전체 지역":region,query||"시설명 전체",type==="all"?"전체 유형":type,zeroWait?"대기 0명":"전체 대기"].join(" · ").slice(0,60);const item={id:createSavedSearchId(),name:savedSearchName.value.trim()||generatedName,region,query,type,zeroWait,savedAt:new Date().toISOString()};const result=saveSavedSearch(item);if(result.ok){savedSearchName.value="";renderSavedSearches();showSavedSearchStatus("검색 조건을 저장했습니다.");}else{const messages={duplicate:"같은 이름과 조건의 검색이 이미 저장되어 있습니다.",limit:"저장 한도(20개)에 도달했습니다. 기존 조건을 삭제한 후 저장하세요.", "storage-unavailable":"브라우저 저장 기능을 사용할 수 없습니다.","storage-error":"브라우저 저장 공간에 기록하지 못했습니다.","invalid":"저장 조건을 확인해주세요."};showSavedSearchStatus(messages[result.reason]||"저장하지 못했습니다.",true);}});
savedSearchList.addEventListener("click",event=>{const loadButton=event.target.closest("button[data-load-saved-search]");if(loadButton){const item=readSavedSearches().find(entry=>entry.id===loadButton.dataset.loadSavedSearch);if(item)applySavedSearch(item);return;}const deleteButton=event.target.closest("button[data-delete-saved-search]");if(deleteButton){const result=removeSavedSearch(deleteButton.dataset.deleteSavedSearch);renderSavedSearches();showSavedSearchStatus(result.ok?"검색 조건을 삭제했습니다.":"검색 조건을 삭제하지 못했습니다.",!result.ok);}});
function showSavedRegionStatus(message,isError=false){savedRegionStatus.textContent=message;savedRegionStatus.className="saved-region-status"+(isError?" error":"");}
function createSavedRegionId(){try{if(typeof crypto!=="undefined"&&crypto.randomUUID)return crypto.randomUUID();}catch{}return Date.now()+"-"+Math.random().toString(36).slice(2,10);}
function renderSavedRegions(){savedRegionList.replaceChildren();const items=readSavedRegions();if(!items.length){const empty=document.createElement("p");empty.className="saved-region-empty";empty.textContent="저장된 관심 지역이 없습니다.";savedRegionList.append(empty);return;}items.forEach(item=>{const row=document.createElement("article");row.className="saved-region-item";const info=document.createElement("div");info.className="saved-region-info";const name=document.createElement("strong");name.textContent=item.region;const meta=document.createElement("small");const date=new Date(item.savedAt);meta.textContent="저장일 "+(Number.isNaN(date.getTime())||date.getTime()===0?"날짜 미확인":date.toLocaleDateString("ko-KR"));info.append(name,meta);const actions=document.createElement("div");actions.className="saved-region-actions";const load=document.createElement("button");load.type="button";load.className="saved-region-load";load.textContent="지역 보기";load.dataset.loadSavedRegion=item.id;load.setAttribute("aria-label",item.region+" 선택");const remove=document.createElement("button");remove.type="button";remove.className="saved-region-delete";remove.textContent="삭제";remove.dataset.deleteSavedRegion=item.id;remove.setAttribute("aria-label",item.region+" 관심 지역 삭제");actions.append(load,remove);row.append(info,actions);savedRegionList.append(row);});}
function applySavedRegion(item){const exists=[...regionSelect.options].some(option=>option.value===item.region);if(!exists){showSavedRegionStatus("저장된 지역을 현재 데이터에서 찾을 수 없습니다.",true);return;}regionSelect.value=item.region;render();showSavedRegionStatus("저장된 관심 지역을 선택했습니다.");}
saveRegionButton.addEventListener("click",()=>{const region=selectedRegion();if(region==="all"){showSavedRegionStatus("전체 지역은 저장할 수 없습니다. 개별 지역을 선택하세요.",true);return;}const result=saveSavedRegion({id:createSavedRegionId(),region,savedAt:new Date().toISOString()});if(result.ok){renderSavedRegions();showSavedRegionStatus("관심 지역을 저장했습니다.");}else{const messages={duplicate:"이미 저장된 관심 지역입니다.","duplicate-id":"저장 식별자가 중복되었습니다. 다시 시도하세요.",limit:"저장 한도(20개)에 도달했습니다. 기존 지역을 삭제한 후 저장하세요.","storage-unavailable":"브라우저 저장 기능을 사용할 수 없습니다.","storage-error":"브라우저 저장 공간에 기록하지 못했습니다.",invalid:"지역 정보를 확인해주세요."};showSavedRegionStatus(messages[result.reason]||"저장하지 못했습니다.",true);}});
savedRegionList.addEventListener("click",event=>{const loadButton=event.target.closest("button[data-load-saved-region]");if(loadButton){const item=readSavedRegions().find(entry=>entry.id===loadButton.dataset.loadSavedRegion);if(item)applySavedRegion(item);return;}const deleteButton=event.target.closest("button[data-delete-saved-region]");if(deleteButton){const result=removeSavedRegion(deleteButton.dataset.deleteSavedRegion);renderSavedRegions();showSavedRegionStatus(result.ok?"관심 지역을 삭제했습니다.":"관심 지역을 삭제하지 못했습니다.",!result.ok);}});
function showSavedFacilityStatus(message,isError=false){savedFacilityStatus.textContent=message;savedFacilityStatus.className="saved-facility-status"+(isError?" error":"");}
function renderSavedFacilities(){
  savedFacilityList.replaceChildren();const items=readSavedFacilities();
  if(!items.length){const empty=document.createElement("p");empty.className="saved-facility-empty";empty.textContent="저장된 관심 시설이 없습니다.";savedFacilityList.append(empty);return;}
  items.forEach(item=>{
    const row=document.createElement("article");row.className="saved-facility-item";
    const info=document.createElement("div");info.className="saved-facility-info";
    const name=document.createElement("strong");name.textContent=item.name;
    const meta=document.createElement("small");meta.textContent=[item.region,item.type].filter(Boolean).join(" · ");
    info.append(name,meta);if(item.address){const address=document.createElement("small");address.textContent=item.address;info.append(address);}
    const actions=document.createElement("div");actions.className="saved-facility-actions";
    const load=document.createElement("button");load.type="button";load.className="saved-facility-load";load.textContent="시설 찾기";load.dataset.loadSavedFacility=item.facilityId;load.setAttribute("aria-label",item.name+" 시설 찾기");
    const remove=document.createElement("button");remove.type="button";remove.className="saved-facility-delete";remove.textContent="삭제";remove.dataset.deleteSavedFacility=item.facilityId;remove.setAttribute("aria-label",item.name+" 관심 시설 삭제");
    actions.append(load,remove);row.append(info,actions);savedFacilityList.append(row);
  });
}
function applySavedFacility(item){
  const current=facilities.find(f=>String(f.facilityId||"")===item.facilityId);
  if(!current){showSavedFacilityStatus("저장된 시설을 현재 데이터에서 찾을 수 없습니다. 데이터가 갱신되었을 수 있습니다.",true);return;}
  const regionExists=[...regionSelect.options].some(option=>option.value===current.region);
  if(!regionExists){showSavedFacilityStatus("저장된 시설의 지역을 현재 데이터에서 찾을 수 없습니다.",true);return;}
  regionSelect.value=current.region;facilitySearch.value=current.name||item.name;typeFilter.value="all";zeroFilter.checked=false;focusedFacilityId=item.facilityId;render();
  const card=[...facilityList.querySelectorAll("article[data-facility-id]")].find(element=>element.dataset.facilityId===item.facilityId);
  card?.scrollIntoView({behavior:"smooth",block:"start"});showSavedFacilityStatus("저장된 시설을 목록에서 찾았습니다.");
}
facilityList.addEventListener("click",event=>{
  const button=event.target.closest("button[data-save-facility]");if(!button)return;
  const facility=facilities.find(f=>String(f.facilityId||"")===button.dataset.saveFacility);if(!facility)return;
  const result=saveSavedFacility({facilityId:facility.facilityId,name:facility.name,region:facility.region,type:facility.type,address:facility.address,savedAt:new Date().toISOString()});
  if(result.ok){renderFacilities();renderSavedFacilities();showSavedFacilityStatus("관심 시설을 저장했습니다.");}
  else{const messages={duplicate:"이미 저장된 관심 시설입니다.",limit:"저장 한도(50개)에 도달했습니다. 기존 시설을 삭제한 후 저장하세요.","storage-unavailable":"브라우저 저장 기능을 사용할 수 없습니다.","storage-error":"브라우저 저장 공간에 기록하지 못했습니다.",invalid:"시설 정보를 확인해주세요."};showSavedFacilityStatus(messages[result.reason]||"저장하지 못했습니다.",true);}
});
savedFacilityList.addEventListener("click",event=>{
  const loadButton=event.target.closest("button[data-load-saved-facility]");if(loadButton){const item=readSavedFacilities().find(entry=>entry.facilityId===loadButton.dataset.loadSavedFacility);if(item)applySavedFacility(item);return;}
  const deleteButton=event.target.closest("button[data-delete-saved-facility]");if(deleteButton){const result=removeSavedFacility(deleteButton.dataset.deleteSavedFacility);renderSavedFacilities();renderFacilities();showSavedFacilityStatus(result.ok?"관심 시설을 삭제했습니다.":"관심 시설을 삭제하지 못했습니다.",!result.ok);}
});
regionSelect.addEventListener("change",()=>{focusedFacilityId=null;render();});facilitySearch.addEventListener("input",()=>{focusedFacilityId=null;renderFacilities();});typeFilter.addEventListener("change",()=>{focusedFacilityId=null;renderFacilities();});zeroFilter.addEventListener("change",()=>{focusedFacilityId=null;renderFacilities();});populateRegions();render();renderSavedSearches();renderSavedRegions();renderSavedFacilities();tryLoadLive();
