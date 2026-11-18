"""伊籍策略：伊籍手牌無上限，止步於「滿血絕不棄 2 抽 1 虧牌」，僅在損血且低價值牌足夠時棄 2 回 1 血。

- 「伊籍-棄2張」若用來抽 1 張牌是淨虧 1 牌差；在損血狀態下應固定選回 1 點血
- 出牌階段先由 ProAgent 打完正常高優牌（含真桃），收尾仍損血且手上有 2 張以上非桃低保值牌才棄 2 回血
- 回合外僅在低血（<=2）且非桃低保值牌足夠時觸發救命，避免每個別人回合都誤觸發

實測勝率（arena_pro.py）：
- 調參集（seed0=0, n=800）：19.4% -> 34.6%（+15.2 個百分點）
- 驗證集（seed0=100000, n=2000）：20.3% -> 34.0%（+13.6 個百分點）
"""

from ai_pro import SkillAct, fn


def _should_heal(agent, g, p):
    if p.hp >= p.maxhp:
        return False
    pool = [c for c in p.all_cards() if fn(c) != "桃"]
    if len(pool) < 2:
        return False
    pool.sort(key=lambda c: agent.keep_val(g, p, c))
    second_kv = agent.keep_val(g, p, pool[1])
    if p.hp <= 1:
        return second_kv <= 90.0
    if p.hp == 2:
        return second_kv <= 78.0
    return second_kv <= 62.0


class Strategy:
    def __init__(self):
        self._busy = False

    def choose_option(self, agent, g, p, skill, labels):
        if skill == "伊籍-棄2張" and p.hp < p.maxhp and len(labels) > 1:
            return 1
        return NotImplemented

    def act(self, agent, g, p, options):
        if self._busy:
            return NotImplemented
        yi_idx = [i for i, (c, t) in enumerate(options) if isinstance(c, SkillAct) and c.name == "伊籍-棄2張"]
        if not yi_idx:
            return NotImplemented

        yi_set = set(yi_idx)
        kept = [(i, opt) for i, opt in enumerate(options) if i not in yi_set]
        if kept:
            self._busy = True
            try:
                r = agent.act(g, p, [opt for _, opt in kept])
            finally:
                self._busy = False
            if r is not None:
                return kept[r][0]

        if _should_heal(agent, g, p):
            return yi_idx[0]
        return None

    def choose_offturn(self, agent, g, p, options, cur, when):
        if self._busy:
            return NotImplemented
        yi_idx = [i for i, (c, t) in enumerate(options) if isinstance(c, SkillAct) and c.name == "伊籍-棄2張"]
        if not yi_idx:
            return NotImplemented

        yi_set = set(yi_idx)
        kept = [(i, opt) for i, opt in enumerate(options) if i not in yi_set]
        if kept:
            self._busy = True
            try:
                r = agent.choose_offturn(g, p, [opt for _, opt in kept], cur, when)
            finally:
                self._busy = False
            if r is not None:
                return kept[r][0]

        if p.hp <= 2 and _should_heal(agent, g, p):
            return yi_idx[0]
        return None
