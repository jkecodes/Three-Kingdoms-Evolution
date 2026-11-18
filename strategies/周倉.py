"""周倉策略：判斷是否值得放棄本回合出基本牌換取「再抽 2 張」階段。

- 通用 AI 對「周倉-再抽牌」一律回傳 True，導致受傷捏桃或手持諸葛連弩／殘血斬殺時仍鎖死所有基本牌
- 僅當「傷時有桃（或可回血酒）」、「距離內有殘血可殺／可收割敵人」、「連弩配雙殺可連殺」或「雙殺將溢出棄牌」時保留基本牌；其餘穩定多抽 2 張拼資源

實測勝率（arena_pro.py）：
- 調參集（seed0=0, n=800）：33.9% -> 36.1%（+2.3 個百分點）
- 驗證集（seed0=100000, n=2000）：34.2% -> 37.2%（+3.0 個百分點）
"""

from ai_pro import is_sha


class Strategy:
    def choose_skill(self, agent, g, p, skill):
        if skill == "周倉-再抽牌":
            if p.hp < p.maxhp and any(c.name == "桃" for c in p.hand):
                return False
            if p.hp <= 2 and any(c.name == "酒" for c in p.hand) and p.char.jiu_self_heal(g, p):
                return False

            shas = sum(1 for c in p.hand if is_sha(c))
            if shas >= 1:
                has_buff = any(c.name in ("酒", "強化") for c in p.hand)
                has_ln = p.has_weapon("諸葛連弩") or any(c.name == "諸葛連弩" for c in p.hand)
                reach = []
                for q in agent.foes_of(g, p):
                    if agent.tscore(g, p, q) <= -100:
                        continue
                    if not (p.char.no_range(g, p) or g.distance(p, q) <= p.attack_range()):
                        continue
                    if p.char.sha_targets(g, p, [q]):
                        reach.append(q)

                if reach:
                    if shas >= 2 and len(p.hand) > p.hp:
                        return False
                    dmg_cap = 1 + (1 if has_buff else 0)
                    for q in reach:
                        ed = agent.expected_dmg(g, p, q, 1, via_sha=True)
                        if ed <= 0:
                            continue
                        if q.hp <= dmg_cap:
                            return False
                        if has_ln and shas >= 2:
                            return False
            return True
        return NotImplemented
