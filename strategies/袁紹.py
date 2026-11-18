"""袁紹策略：抽牌選 4 張（放棄殺限）並將「閃」轉為「萬箭齊發」擴大群傷。

- 「袁紹-多抽2張」幾乎恆開（僅在手持諸葛連弩且 >= 2 張殺時保留殺）
- 先由預設邏輯出完高優先牌（無中生有、桃、裝備、單體控制），再評估是否以「閃」轉「萬箭齊發」
- 過濾 0 傷（如藤甲/緩衝盾）、忠臣誤殺低血主公、敵方鄧艾低血反噬與低血保留最後一閃

實測勝率（arena_pro.py）：
- 調參集（seed0=0, n=800）：36.8% -> 38.1%（+1.4 個百分點）
- 驗證集（seed0=100000, n=2000）：36.3% -> 38.5%（+2.2 個百分點）
"""

from ai_pro import SkillAct, is_sha


def _wan_score(agent, g, p):
    net = 0.0
    foe_hits = 0
    for q in g.others(p):
        ed = agent.expected_dmg(g, p, q, 1)
        if ed <= 0:
            continue
        att = agent.attitude(g, p, q)
        if att < 0:
            foe_hits += 1
            s = 1.0
            if q.hp <= ed:
                s += 1.2
            if len(q.hand) <= 1:
                s += 0.4
            if p.role == "反賊" and q.role == "主公":
                s += 0.4
            net += s
        elif att >= 1:
            if p.role == "忠臣" and q.role == "主公" and (q.hp <= 1 or (q.hp <= 2 and len(q.hand) <= 2)):
                return 0, -999.0
            if ed >= q.hp and len(q.hand) <= 1:
                net -= 2.2
            elif p.role == "忠臣" and q.role == "主公":
                net -= (1.2 if q.hp <= 3 or len(q.hand) <= 2 else 0.75)
            elif len(q.hand) == 0:
                net -= 0.85
            else:
                net -= 0.45
    return foe_hits, net


class Strategy:
    def __init__(self):
        self._busy = False

    def choose_skill(self, agent, g, p, skill):
        if skill == "袁紹-多抽2張":
            w = p.equip["weapon"]
            if w and w.name == "諸葛連弩" and sum(1 for c in p.hand if is_sha(c)) >= 2 and agent.foes_of(g, p):
                return False
            return True
        return NotImplemented

    def act(self, agent, g, p, options):
        if self._busy:
            return NotImplemented
        vs = [i for i, (c, t) in enumerate(options)
              if not isinstance(c, SkillAct) and c.name == "萬"
              and getattr(c, "orig", None) is not None]
        if not vs:
            return NotImplemented

        self._busy = True
        try:
            r = agent.act(g, p, options)
        finally:
            self._busy = False
        if r is not None:
            return r

        # 敵方鄧艾存在時，1 血不盲開錦囊自殺
        if p.hp <= 1 and any(
            q.char.name == "鄧艾" and agent.attitude(g, p, q) < 0
            and g.dmg_preview(q, 1, tgt=p) > 0
            for q in g.others(p)
        ):
            return None

        foe_hits, net = _wan_score(agent, g, p)
        if foe_hits <= 0:
            return None

        excess = len(p.hand) > p.hp
        if not excess and p.hp <= 2 and len(vs) == 1 and agent.foes_of(g, p):
            if foe_hits < 2 or net < 2.2:
                return None
        elif excess:
            if net < 0.35:
                return None
        elif net < 1.0:
            return None

        return min(vs, key=lambda idx: agent.keep_val(g, p, options[idx][0]))
