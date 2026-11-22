export const SAVED_FACILITIES_KEY = "childcare-map:saved-facilities:v1";
export const MAX_SAVED_FACILITIES = 50;
function resolveStorage(storage) { if (storage !== undefined) return storage; try { return globalThis.localStorage || null; } catch { return null; } }
function boundedText(value, maxLength, required = false) { if (value == null) return required ? null : ""; if (typeof value !== "string") return null; const normalized = value.trim(); if ((required && !normalized) || normalized.length > maxLength || /[\u0000-\u001f\u007f]/.test(normalized)) return null; return normalized; }
function normalizeSavedFacility(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  const facilityId=boundedText(value.facilityId,160,true),name=boundedText(value.name,120,true),region=boundedText(value.region,100,true),type=boundedText(value.type,60),address=boundedText(value.address,300);
  if(facilityId===null||name===null||region===null||type===null||address===null)return null;
  const savedAt=typeof value.savedAt==="string"&&Number.isFinite(Date.parse(value.savedAt))?value.savedAt:new Date(0).toISOString();
  return{facilityId,name,region,type,address,savedAt};
}
function readStoredItems(target){
  try{const raw=target.getItem(SAVED_FACILITIES_KEY);if(!raw)return{ok:true,items:[]};let parsed;try{parsed=JSON.parse(raw);}catch{return{ok:true,items:[]};}if(!Array.isArray(parsed))return{ok:true,items:[]};const seenIds=new Set(),items=[];for(const entry of parsed){const item=normalizeSavedFacility(entry);if(!item||seenIds.has(item.facilityId))continue;seenIds.add(item.facilityId);items.push(item);if(items.length>=MAX_SAVED_FACILITIES)break;}return{ok:true,items};}catch{return{ok:false,items:[]};}
}
export function readSavedFacilities(storage){const target=resolveStorage(storage);return target?readStoredItems(target).items:[];}
export function saveSavedFacility(value,storage){
  const target=resolveStorage(storage);if(!target)return{ok:false,reason:"storage-unavailable",items:[]};
  const item=normalizeSavedFacility(value);if(!item)return{ok:false,reason:"invalid",items:readSavedFacilities(target)};
  const stored=readStoredItems(target);if(!stored.ok)return{ok:false,reason:"storage-error",items:[]};
  const current=stored.items;if(current.some(existing=>existing.facilityId===item.facilityId))return{ok:false,reason:"duplicate",items:current};
  if(current.length>=MAX_SAVED_FACILITIES)return{ok:false,reason:"limit",items:current};
  const items=[item,...current];try{target.setItem(SAVED_FACILITIES_KEY,JSON.stringify(items));return{ok:true,items};}catch{return{ok:false,reason:"storage-error",items:current};}
}
export function removeSavedFacility(facilityId,storage){
  const target=resolveStorage(storage);if(!target)return{ok:false,reason:"storage-unavailable",items:[]};
  const stored=readStoredItems(target);if(!stored.ok)return{ok:false,reason:"storage-error",items:[]};
  const current=stored.items,items=current.filter(item=>item.facilityId!==facilityId);if(items.length===current.length)return{ok:false,reason:"not-found",items:current};
  try{target.setItem(SAVED_FACILITIES_KEY,JSON.stringify(items));return{ok:true,items};}catch{return{ok:false,reason:"storage-error",items:current};}
}
