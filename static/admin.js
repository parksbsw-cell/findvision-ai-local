const token = document.querySelector("#token");
const status = document.querySelector("#status");
const stats = document.querySelector("#stats");
const labels = {
  visits: "전체 방문 횟수", visitors: "순 방문자",
  returning_visitors: "재방문자", retention_percent: "재방문율",
  generated: "이미지 생성 횟수", visitors_7d: "최근 7일 방문자",
  returning_days: "누적 재방문 일수", d1_retention_percent: "D1 리텐션",
  d7_retention_percent: "D7 리텐션", generation_conversion_percent: "생성 전환율",
};

document.querySelector("#load").addEventListener("click", async () => {
  status.textContent = "불러오는 중…";
  stats.classList.add("hidden");
  try {
    const response = await fetch("/api/admin/stats", {headers: {"X-Admin-Token": token.value}});
    if (!response.ok) throw new Error("관리자 토큰을 확인하세요.");
    const data = await response.json();
    stats.replaceChildren(...Object.entries(labels).map(([key, label]) => {
      const card = document.createElement("article");
      const value = key.endsWith("_percent") ? `${data[key]}%` : data[key];
      const strong = document.createElement("strong");
      const span = document.createElement("span");
      strong.textContent = value;
      span.textContent = label;
      card.append(strong, span);
      return card;
    }));
    stats.classList.remove("hidden");
    status.textContent = "";
    token.value = "";
  } catch (error) { status.textContent = error.message; }
});
