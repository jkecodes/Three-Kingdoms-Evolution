# 音樂與音效 (web/audio/)

- `manifest.json` 決定哪個音效代號用哪個檔案;沒列在 manifest 的音效,遊戲會用程式合成的音效頂著。
- `bgm/` 背景音樂 (mp3,建議 100~128 kbps,單曲 2~4 MB);`se/` 音效 (mp3 / ogg / wav,越短越好)。
- 音效代號: card slash dodge hit fire thunder heal equip trick duel ping turn death judgeR judgeB draw discard flip disguise rankup rankdown pickOpen pickChoose gameStart arena win
- BGM 狀態: `lobby` (大廳、選武將、結算後)、`battle` (對戰進行中)。同一狀態列多首會隨機挑一首。
- 新增 / 換檔之後,把 manifest.json 的 `v` 加 1。
- **授權**: 每個來源都要在 manifest 的 `credits` 寫清楚 (遊戲設定裡的「音樂與音效來源」會自動顯示)。
  - 魔王魂: 商用 OK、免報備,表記「音楽：魔王魂」;禁止把音檔單獨再散布 / 販售、禁止 AI 學習 / AI 改編。
  - BBC Sound Effects (RemArc) 只能個人 / 教育 / 研究,不可用在公開上線的遊戲,不要放。
