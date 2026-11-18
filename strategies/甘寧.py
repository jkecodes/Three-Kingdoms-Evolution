"""甘寧策略：靈活將多餘或出牌後滯留的基本牌轉成「無中生有」。

- 開局若有「冗餘基本牌」（>=2 張閃、或>=3 血且非唯一防禦閃、或非連弩時的>=2 張殺），直接先轉無中生有放大手牌資訊
- 否則先由 ProAgent 打完桃、裝備、酒殺/可用殺與控制牌；收尾仍有剩餘基本牌（避開傷時所需桃）再轉無中生有
- 敵方有鄧艾且自身僅 1 血時不主動開錦囊自傷

實測勝率（arena_pro.py）：
- 調參集（seed0=0, n=800）：26.8% -> 27.9%（+1.1 個百分點）
- 驗證集（seed0=100000, n=2000）：27.6% -> 29.3%（+1.7 個百分點）
"""

from ai_pro import SkillAct


def _has_deng_ai_risk(agent, g, p):
    return p.hp <= 1 and any(
        q.char.name == "鄧艾" and agent.attitude(g, p, q) < 0
        and g.dmg_preview(q, 1, tgt=p) > 0
        for q in g.others(p)
    )


class Strategy:
    def __init__(self):
        self._busy = False

    def act(self, agent, g, p, options):
        if self._busy or p.turn_flags.get("gn"):
            return NotImplemented

        vs = [i for i, (c, t) in enumerate(options)
              if not isinstance(c, SkillAct) and c.name == "無"
              and getattr(c, "orig", None) is not None]
        if not vs or _has_deng_ai_risk(agent, g, p):
            return NotImplemented

        need_peach = p.hp < p.maxhp or any(
            agent.attitude(g, p, q) >= 1 and q.hp <= 1 for q in g.others(p)
        )
        peaches = sum(1 for c in p.hand if c.name == "桃")
        shas = sum(1 for c in p.hand if c.kind == "basic" and "殺" in c.name)
        shans = sum(1 for c in p.hand if c.name == "閃")
        has_ln = bool(p.equip["weapon"] and p.equip["weapon"].name == "諸葛連弩")
        has_jiu_or_buff = any(c.name in ("酒", "強化") for c in p.hand) or g.jiu > 0

        # 階段 1：不影響本回合進攻節奏的冗餘基本牌，開局先轉無中生有抽 2 張
        early = []
        for i in vs:
            on = options[i][0].orig.name
            if on == "閃" and (shans >= 2 or p.hp >= 3):
                early.append(i)
            elif "殺" in on and shas >= 2 and not has_ln:
                early.append(i)
            elif on == "桃" and not need_peach and peaches >= 2:
                early.append(i)
        if early:
            return min(early, key=lambda idx: agent.keep_val(g, p, options[idx][0]))

        # 階段 2：先委派 ProAgent 打出單殺、酒殺、桃、裝備與其他高優牌（過濾 ViewCard("無")）
        vset = set(vs)
        kept = [(i, opt) for i, opt in enumerate(options) if i not in vset]
        if kept:
            self._busy = True
            try:
                r = agent.act(g, p, [opt for _, opt in kept])
            finally:
                self._busy = False
            if r is not None:
                return kept[r][0]

        # 階段 3：ProAgent 無牌可出後，把滯留殺/酒/多餘閃（避開關鍵保命桃或唯一連招）轉成無中生有
        late = []
        for i in vs:
            on = options[i][0].orig.name
            if on == "桃" and (need_peach or (peaches <= 1 and len(p.hand) <= p.hp)):
                continue
            if on == "閃" and p.hp <= 2 and shans <= 1 and len(p.hand) <= p.hp and agent.foes_of(g, p):
                continue
            if on == "酒" and has_jiu_or_buff and shas >= 1 and p.hp <= 2:
                continue
            late.append(i)
        if not late:
            return None
        return min(late, key=lambda idx: agent.keep_val(g, p, options[idx][0]))
