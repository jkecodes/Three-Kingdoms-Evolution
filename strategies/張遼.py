"""張遼策略：出「殺全部人」前先補齊進攻武器與「無中生有」，出牌收尾無防具時以低價值/溢出牌轉化防具。

- 若手上有「無中生有」或可裝進空武器欄的「青釭劍／貫石斧／流星錘／孔雀羽扇／古錠刀／雌雄雙股劍」，先委派 ProAgent 打出／裝備後再觸發「張遼-殺全部人」（注意不能先喝「酒」，因 jiu_must 會鎖定僅限單體殺）
- 過濾防具 ViewCard 後再委派 ProAgent，避免其依原牌名誤觸發轉化
- 常規出牌結束且防具欄為空時：手牌即將溢出或有低價值滯留牌（避開桃與反制牌、敵青釭與孤閃轉仁王）即補上「八卦陣」／「仁王盾」

實測勝率（arena_pro.py）：
- 調參集（seed0=0, n=800）：27.6% -> 30.5%（+2.9 個百分點）
- 驗證集（seed0=100000, n=2000）：26.2% -> 28.2%（+2.0 個百分點）
"""

import os
from ai_pro import SkillAct, fn

TH = float(os.environ.get("ZL_TH", "78"))
PREP_WEAPONS = {"青釭劍", "貫石斧", "流星錘", "孔雀羽扇", "古錠刀", "雌雄雙股劍"}


class Strategy:
    def __init__(self):
        self._busy = False

    def act(self, agent, g, p, options):
        if self._busy:
            return NotImplemented

        armor_views = [
            i for i, (c, t) in enumerate(options)
            if not isinstance(c, SkillAct)
            and c.name in ("八卦陣", "仁王盾")
            and getattr(c, "orig", None) is not None
        ]
        armor_set = set(armor_views)

        # 若同時有「張遼-殺全部人」與可前置打出的無中生有／強攻空欄武器，先打出前置牌再全體殺
        has_all_sha = any(isinstance(c, SkillAct) and c.name == "張遼-殺全部人" for c, _ in options)
        if has_all_sha:
            need_weapon = p.equip["weapon"] is None and not g.equip_off()
            has_prep = any(
                not isinstance(c, SkillAct)
                and getattr(c, "orig", None) is None
                and (fn(c) == "無中生有" or (need_weapon and fn(c) in PREP_WEAPONS))
                for c, _ in options
            )
            if has_prep:
                kept_prep = [
                    (i, opt) for i, opt in enumerate(options)
                    if i not in armor_set
                    and not (isinstance(opt[0], SkillAct) and opt[0].name == "張遼-殺全部人")
                ]
                if kept_prep:
                    self._busy = True
                    try:
                        r = agent.act(g, p, [opt for _, opt in kept_prep])
                    finally:
                        self._busy = False
                    if r is not None:
                        return kept_prep[r][0]

        if not armor_views or p.equip["armor"] is not None or g.equip_off():
            kept_no_armor = [(i, opt) for i, opt in enumerate(options) if i not in armor_set]
            if len(kept_no_armor) == len(options):
                return NotImplemented
            self._busy = True
            try:
                r = agent.act(g, p, [opt for _, opt in kept_no_armor])
            finally:
                self._busy = False
            return kept_no_armor[r][0] if r is not None else None

        # 委派 ProAgent 時暫時排除防具 ViewCard，避免混淆
        kept = [(i, opt) for i, opt in enumerate(options) if i not in armor_set]
        if kept:
            self._busy = True
            try:
                r = agent.act(g, p, [opt for _, opt in kept])
            finally:
                self._busy = False
            if r is not None:
                return kept[r][0]

        excess = len(p.hand) > p.hp
        shans = sum(1 for c in p.hand if fn(c) == "閃")
        enemy_qinggang = any(
            q.has_weapon("青釭劍") and agent.attitude(g, p, q) < 0
            for q in g.others(p)
        )
        best_i = None
        best_score = 1e9
        keep_offturn = {"桃", "無懈可擊", "反擊", "調虎離山", "占卜", "偽裝", "隔岸觀火"}
        for i in armor_views:
            c = options[i][0]
            orig_n = fn(c.orig)
            if orig_n in keep_offturn:
                if orig_n in ("反擊", "調虎離山", "占卜", "隔岸觀火") and excess:
                    pass
                else:
                    continue
            # 敵方持有青釭劍無視防具，或僅剩最後一閃且轉黑仁王盾時，不拿唯一閃換防具
            if orig_n == "閃" and not excess and shans <= 1:
                if enemy_qinggang or c.name == "仁王盾":
                    continue
            kv = agent.keep_val(g, p, c)
            limit = 95.0 if excess else TH
            if kv <= limit:
                # 同價值時優先紅牌變「八卦陣」（泛用擋紅黑殺）
                score = kv - (1.5 if c.name == "八卦陣" else 0.0)
                if score < best_score:
                    best_score = score
                    best_i = i
        return best_i
