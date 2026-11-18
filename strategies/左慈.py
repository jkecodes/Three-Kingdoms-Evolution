"""左慈策略：依場上血線與手牌情境從候選池挑選高強度化身，並僅在淨收益為正時全部翻面。

- 原本 choose_option("左慈-化身") 走通用預設會只挑名單順位第 0/1 位，錯失華雄、孫策、龐統、袁紹、劉協等強將
- 針對殘血保命（龐統／華佗／劉備／張角）、缺牌補充（華雄／袁紹／孫策／孔融）與減傷控制（劉協／典韋／曹真／司馬昭）動態評分挑將
- 「左慈-全部翻面」僅在能翻面的未翻面敵人多於盟友（含自身）時發動

實測勝率（arena_pro.py）：
- 調參集（seed0=0, n=800）：35.2% -> 42.9%（+7.6 個百分點）
- 驗證集（seed0=100000, n=2000）：34.8% -> 42.8%（+8.0 個百分點）
"""

BASE_TIER = {
    "華雄": 95,
    "孫策": 92,
    "袁紹": 88,
    "司馬昭": 86,
    "曹操": 85,
    "劉協": 84,
    "典韋": 82,
    "龐統": 82,
    "曹真": 80,
    "呂布": 78,
    "荀彧": 78,
    "馬超": 76,
    "夏侯惇": 74,
    "甘寧": 74,
    "曹丕": 74,
    "李儒": 72,
    "郭嘉": 72,
    "崔琰": 72,
    "太史慈": 72,
    "周魴": 70,
    "孔融": 70,
    "華佗": 70,
    "張角": 68,
    "鄧艾": 68,
    "關羽": 66,
    "劉備": 64,
    "張遼": 64,
    "黃蓋": 62,
    "許褚": 56,
    "曹植": 45,
    "蔣幹": 40,
    "伊籍": 38,
    "孟獲": 35,
    "公孫淵": 30,
    "袁術": 25,
    "董卓": 20,
}


def _alias_score(agent, g, p, nm):
    s = float(BASE_TIER.get(nm, 55))
    if nm == "龐統":
        s = 98.0 if p.hp <= 2 else 86.0
    elif nm == "華佗" and p.hp <= 2:
        s = 88.0
    elif nm == "劉備" and p.hp <= 2:
        s = 86.0
    elif nm == "張角" and p.hp < p.maxhp and len(p.hand) >= 3:
        s = 86.0
    elif nm == "關羽" and p.hp < p.maxhp:
        s = 76.0
    elif nm == "孔融" and len(p.hand) >= 3:
        s = 86.0
    elif nm == "諸葛亮":
        s = 84.0 if len(p.hand) <= 1 else 68.0
    elif nm == "周魴" and p.hp <= 2:
        s = 78.0
    elif nm == "張遼" and len(agent.foes_of(g, p)) >= 2:
        s = 78.0
    elif nm == "許褚":
        shas = sum(1 for c in p.hand if "殺" in c.name or c.name == "決")
        s = 72.0 if shas >= 2 else 50.0
    elif nm == "黃蓋" and p.hp <= 2:
        s = 32.0
    return s


class Strategy:
    def choose_option(self, agent, g, p, skill, labels):
        if skill == "左慈-化身" and labels:
            return max(range(len(labels)), key=lambda i: _alias_score(agent, g, p, labels[i]))
        return NotImplemented

    def choose_skill(self, agent, g, p, skill):
        if skill == "左慈-全部翻面":
            foes_unflipped = sum(
                1 for q in g.others(p)
                if not q.flipped and agent.attitude(g, p, q) < 0
            )
            allies_unflipped = sum(
                1 for q in g.others(p)
                if not q.flipped and agent.attitude(g, p, q) >= 1
            )
            self_term = 1 if p.flipped else -1
            return (foes_unflipped - allies_unflipped + self_term) > 0
        return NotImplemented
