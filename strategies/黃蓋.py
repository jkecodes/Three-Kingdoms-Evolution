"""黃蓋策略：善用「苦肉」補牌與將剩餘／被防具擋住的「殺」轉為「過河拆橋」。

- 先由預設邏輯出完桃、無中生有、裝備、可用殺與其他高優牌
- 預設出牌結束後，將多餘的「殺」轉成「過河拆橋」拆隊友判定牌（樂/兵）或敵方關鍵防具/武器/手牌
- 無傷來源的免費「苦肉」最多補觸發 2 次（防無限循環），其餘依血線與手牌決定

實測勝率（arena_pro.py）：
- 調參集（seed0=0, n=800）：28.5% -> 31.8%（+3.3 個百分點）
- 驗證集（seed0=100000, n=2000）：27.5% -> 29.3%（+1.8 個百分點）
"""

from ai_pro import SkillAct


def _chai_score(agent, g, p, t):
    if not (t.hand or any(t.equip.values()) or t.judge):
        return -999.0
    att = agent.attitude(g, p, t)
    if att >= 1:
        if t.judge:
            return 120.0 + (25.0 if t.role == "主公" else 0.0)
        return -999.0
    ts = agent.tscore(g, p, t)
    if ts <= -100:
        return -999.0
    # 避免單手牌敵方陸遜免費觸發連營
    if t.char.name == "陸遜" and len(t.hand) == 1 and not any(t.equip.values()) and not t.judge:
        return -999.0
    s = ts
    if t.equip["armor"] or t.equip["armor2"] or t.equip["h+"]:
        s += 45.0
    w = t.equip["weapon"]
    if w and w.name == "諸葛連弩":
        s += 55.0
    elif w:
        s += 20.0
    if len(t.hand) <= 2:
        s += 15.0
    return s


class Strategy:
    def __init__(self):
        self._busy = False
        self._free_turn = -1
        self._free_cnt = 0

    def act(self, agent, g, p, options):
        if self._busy:
            return NotImplemented

        # 1. 若有免費無傷苦肉（例如減傷/免疫護盾），限量觸發
        if g.dmg_preview(None, 1, tgt=p) == 0 and len(p.hand) < 6:
            if self._free_turn != g.turn_id:
                self._free_turn = g.turn_id
                self._free_cnt = 0
            if self._free_cnt < 2:
                for i, (c, t) in enumerate(options):
                    if isinstance(c, SkillAct) and c.name == "黃蓋-苦肉":
                        self._free_cnt += 1
                        return i

        # 2. 先交由 ProAgent 處理常規出牌（桃、無中、殺、裝備等）
        self._busy = True
        try:
            r = agent.act(g, p, options)
        finally:
            self._busy = False
        if r is not None:
            return r

        # 3. 剩餘的「殺」轉成「過河拆橋」（避開低血鄧艾自傷）
        deng_ai_risk = p.hp <= 1 and any(
            q.char.name == "鄧艾" and agent.attitude(g, p, q) < 0
            and g.dmg_preview(q, 1, tgt=p) > 0
            for q in g.others(p)
        )
        if not deng_ai_risk:
            best = None
            best_s = 0.0
            for i, (c, t) in enumerate(options):
                if not isinstance(c, SkillAct) and c.name == "過" and getattr(c, "orig", None) is not None and t is not None:
                    s = _chai_score(agent, g, p, t)
                    if s > best_s:
                        best_s = s
                        best = i
            if best is not None:
                return best

        # 4. 仍有連弩或多牌需求且血量充裕時才考慮額外苦肉
        w = p.equip["weapon"]
        if p.hp >= 3 and len(p.hand) <= 2:
            for i, (c, t) in enumerate(options):
                if isinstance(c, SkillAct) and c.name == "黃蓋-苦肉":
                    return i
        if w and w.name == "諸葛連弩" and p.hp >= 3 and len(p.hand) <= 3:
            for i, (c, t) in enumerate(options):
                if isinstance(c, SkillAct) and c.name == "黃蓋-苦肉":
                    return i
        return None
