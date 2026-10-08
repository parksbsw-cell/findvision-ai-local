const $ = id => document.getElementById(id);
let appearance = null;
const labels = {name:'이름',gender:'성별',age:'나이',height:'키(cm)',weight:'몸무게(kg)',body_type:'체형',hair:'머리',top:'상의',outerwear:'외투·겉옷',bottom:'하의',shoes:'신발',hat:'모자',glasses:'안경',facial_hair:'수염',accessories:'소지품·액세서리',last_seen:'마지막 목격 위치'};

function status(text, error=false) {
  $('status').textContent = text;
  $('status').style.color = error ? '#b42318' : '#334155';
}

async function responseData(response) {
  const type = response.headers.get('content-type') || '';
  return type.includes('application/json') ? response.json() : {detail:'서버 응답을 읽지 못했습니다.'};
}

function renderFacts() {
  $('facts').replaceChildren(...Object.entries(appearance).map(([key, value]) => {
    const wrap = document.createElement('label');
    wrap.className = 'fact-field';
    const title = document.createElement('span');
    title.textContent = labels[key] || key;
    const input = document.createElement('input');
    input.value = Array.isArray(value) ? value.join(', ') : value;
    input.placeholder = '정보 없음';
    input.addEventListener('input', () => {
      appearance[key] = Array.isArray(value)
        ? input.value.split(',').map(item => item.trim()).filter(Boolean)
        : input.value.trim();
    });
    wrap.append(title, input);
    return wrap;
  }));
}

$('analyze').onclick = async () => {
  const message = $('message').value.trim();
  if (!message) return status('문자를 입력하세요.', true);
  status('분석 중…');
  let response;
  try { response = await fetch('/api/analyze', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message})}); }
  catch { return status('로컬 서버에 연결할 수 없습니다.', true); }
  const data = await responseData(response);
  if (!response.ok) return status(data.detail || '분석 실패', true);
  appearance = data.appearance;
  renderFacts();
  $('analysis').classList.remove('hidden');
  $('generate').disabled = !data.is_missing_alert;
  status(data.is_missing_alert ? '실종 재난문자로 확인했습니다. 분석 결과를 확인한 뒤 이미지를 생성하세요.' : data.warnings.join(' '), !data.is_missing_alert);
};

async function generate() {
  const message = $('message').value.trim();
  if (!appearance) return status('먼저 내용을 분석하세요.', true);
  status('로컬 AI가 후보를 생성하고 인물·의복·소지품을 각각 검수 중입니다…');
  $('generate').disabled = true;
  $('regenerate').disabled = true;
  let response;
  try { response = await fetch('/api/generate', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message, appearance})}); }
  catch { $('generate').disabled=false;$('regenerate').disabled=false;return status('로컬 서버 연결이 끊겼습니다.', true); }
  const data = await responseData(response);
  $('generate').disabled = false;
  $('regenerate').disabled = false;
  if (!response.ok) return status(data.detail || '생성 실패', true);
  const src = `data:${data.mime_type};base64,${data.image_base64}`;
  $('original').textContent = message;
  $('image').src = src;
  const verdict = data.verification.passed ? '검수 통과' : '검수 미통과';
  const details = data.verification.wrong?.length ? ` · ${data.verification.wrong.join(' / ')}` : '';
  $('verification').textContent = `${data.attempts}개 후보 생성 · AI 3회 검수 · ${verdict} ${data.verification.score}점${details}`;
  $('result').classList.remove('hidden');
  $('popup-message').textContent = message;
  $('popup-image').src = src;
  $('popup').showModal();
  status(
    data.verification.passed
      ? '생성과 검수를 완료했습니다.'
      : '가장 가까운 이미지를 표시했습니다. 일부 조건이 맞지 않아 다시 생성을 권장합니다.',
    !data.verification.passed
  );
}

$('generate').onclick = generate;
$('regenerate').onclick = generate;
$('close-popup').onclick = () => $('popup').close();
