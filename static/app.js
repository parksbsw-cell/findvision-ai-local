const $=id=>document.getElementById(id);let appearance=null;
function status(text,error=false){$('status').textContent=text;$('status').style.color=error?'#b42318':'#334155'}
$('analyze').onclick=async()=>{const message=$('message').value.trim();if(!message)return status('문자를 입력하세요.',true);status('분석 중…');
  const r=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message})});
  const d=await r.json();if(!r.ok)return status(d.detail||'분석 실패',true);appearance=d.appearance;
  $('facts').replaceChildren(...Object.entries(appearance).filter(([,v])=>Array.isArray(v)?v.length:v).map(([k,v])=>{const e=document.createElement('span');e.className='fact';e.textContent=`${k}: ${Array.isArray(v)?v.join(', '):v}`;return e}));
  $('analysis').classList.remove('hidden');$('generate').disabled=!d.is_missing_alert;status(d.is_missing_alert?'실종 재난문자로 확인했습니다.':d.warnings.join(' '),!d.is_missing_alert)};
$('generate').onclick=async()=>{const message=$('message').value.trim();status('로컬 AI가 생성하고 최대 3회 검수 중입니다…');$('generate').disabled=true;
  const r=await fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message,appearance})});const d=await r.json();$('generate').disabled=false;
  if(!r.ok)return status(d.detail||'생성 실패',true);const src=`data:${d.mime_type};base64,${d.image_base64}`;
  $('original').textContent=message;$('image').src=src;$('verification').textContent=`${d.attempts}회 생성 · 검수 ${d.verification.score}점`;$('result').classList.remove('hidden');
  $('popup-message').textContent=message;$('popup-image').src=src;$('popup').showModal();status('생성과 검수를 완료했습니다.')};
$('close-popup').onclick=()=>$('popup').close();

