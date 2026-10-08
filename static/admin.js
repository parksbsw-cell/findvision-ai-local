const token = document.querySelector("#token");
const status = document.querySelector("#status");
const stats = document.querySelector("#stats");
const labels = {
  visits: "전체 방문 횟수", unique_visitors: "순 방문자",
  returning_visitors: "재방문자", retention_percent: "재방문율",
  generations: "이미지 생성 횟수", visitors_last_7_days: "최근 7일 방문자",
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
      const value = key === "retention_percent" ? `${data[key]}%` : data[key];
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
