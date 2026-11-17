"""無懈可擊的利害摘要: 把「誰對誰用了什麼牌」翻成「誰即將得到 / 失去什麼」,並標出敵方 / 友方 / 身分不明。
只用玩家本來就看得到的資訊 (自己的身分、已公開的身分),不會洩漏暗牌。"""
from engine import Player


def _side(role):
    if role in ("主公", "忠臣"):
        return "A"
    if role == "反賊":
        return "B"
    if role == "內奸":
        return "N"
    if role[:1] in ("紅", "藍"):
        return role[:1]
    return None


def label(g, p, x):
    """x 在 p 眼中是誰: 你 / 敵方 P2(反賊/張遼) / 友方 P1(忠臣/…) / 身分不明的 P3(?…)"""
    if x is p:
        return "你"
    name = x.name
    role = g.revealed.get(x.idx)
    if role is None:
        return f"身分不明的{name}"
    sp, sx = _side(p.role), _side(role)
    rel = "" if sp in (None, "N") or sx in (None, "N") else ("友方" if sp == sx else "敵方")
    return f"{rel}{name}"   # 名字本身已帶身分 (P0(主公/劉禪));沒公開的由伺服器的 fog_text 統一遮成 (?)


# 牌 → (中文樣板, 英文, 日文);{S} = 出牌的人,{T} = 受影響的人。樣板同時給前端翻譯 (見 web/i18n_ui.js,由 i18n_lines() 產生)
T = {
    "順": ("{S}即將從{T}身上拿走 1 張牌", "{S} is about to take a card from {T}", "{S}が{T}から1枚奪おうとしています"),
    "過": ("{S}即將讓{T}被棄置 1 張牌", "{S} is about to make {T} discard a card", "{S}が{T}に1枚捨てさせようとしています"),
    "決": ("{S}即將和{T}決鬥 (先不出殺的 −1 體力)", "{S} is about to duel {T} (first to fail to play Attack loses 1 HP)", "{S}が{T}と決闘しようとしています(先に殺を出せない方が体力-1)"),
    "火攻": ("{S}即將對{T}發動火攻 (可能受到 1 點火焰傷害)", "{S} is about to use Fire Attack on {T} (may deal 1 fire damage)", "{S}が{T}に火攻を使おうとしています(火炎ダメージ1の可能性)"),
    "借": ("{S}即將讓{T}出殺,否則武器被奪走", "{S} is about to make {T} play Attack, or lose their weapon", "{S}が{T}に殺を出させようとしています。出せなければ武器を奪われます"),
    "無": ("{S}即將抽 2 張牌", "{S} is about to draw 2 cards", "{S}が2枚引こうとしています"),
    "桃園": ("{T}即將回復 1 點體力", "{T} is about to recover 1 HP", "{T}が体力を1回復しようとしています"),
    "增": ("{S}即將抽 3 張牌 (之後棄 1~2 張)", "{S} is about to draw 3 cards (then discard 1-2)", "{S}が3枚引こうとしています(その後1〜2枚捨てる)"),
    "拋": ("{S}即將讓{T}棄 1 張牌,自己抽 1 張", "{S} is about to make {T} discard 1 card and draw 1", "{S}が{T}に1枚捨てさせ、自分は1枚引こうとしています"),
    "笑": ("{S}即將給{T}一張牌並對其造成 1 點傷害", "{S} is about to give {T} a card and deal 1 damage", "{S}が{T}に1枚渡して1ダメージを与えようとしています"),
    "鴻": ("{S}即將和{T}各抽 1 張比顏色 (同色: 雙方棄掉,對方 −1 體力)", "{S} is about to compare colors with {T} (same color: both discard, they lose 1 HP)", "{S}が{T}と色比べをしようとしています(同色: 両者捨て、相手の体力-1)"),
    "投": ("{S}即將抽 1 張牌,並讓{T}回復 1 點體力", "{S} is about to draw 1 card and heal {T} by 1", "{S}が1枚引き、{T}の体力を1回復しようとしています"),
    "五": ("{S}即將翻開牌,全場輪流各拿 1 張", "{S} is about to reveal cards for everyone to take one", "{S}がカードを公開し、全員が順に1枚取ろうとしています"),
    "漁": ("{S}即將盯上{T}: 他每用一張錦囊,使用者就抽 1 張", "{S} is about to target {T}: they draw 1 card per trick {T} plays", "{S}が{T}を狙おうとしています: {T}が錦囊を使うたびに1枚引きます"),
    "偽": ("{S}即將偽裝成另一位武將", "{S} is about to disguise as another hero", "{S}が別の武将に変装しようとしています"),
    "未": ("{S}即將抽 2 張牌 (下個回合才入手)", "{S} is about to draw 2 cards (received next turn)", "{S}が2枚引こうとしています(次のターンに手札へ)"),
    "發": ("{S}即將抽 1~5 張牌 (回合結束再付代價)", "{S} is about to draw 1-5 cards (pays the price at end of turn)", "{S}が1〜5枚引こうとしています(ターン終了時に代償)"),
    "孤": ("{S}即將發動孤注一擲 (判定: 抽牌或棄光手牌)", "{S} is about to gamble (judgement: draw cards or discard the whole hand)", "{S}が一か八かを使おうとしています(判定: 引くか手札を全て捨てる)"),
    "鐵": ("{S}即將橫置兩名武將 (連鎖傷害)", "{S} is about to chain two heroes (linked damage)", "{S}が2人の武将を横置しようとしています(連鎖ダメージ)"),
    "聲": ("{S}即將把牌轉交給{T}", "{S} is about to pass cards to {T}", "{S}が{T}にカードを渡そうとしています"),
    "出": ("{S}即將轉移場上的延時錦囊", "{S} is about to move a delayed trick on the table", "{S}が場の遅延錦囊を移そうとしています"),
    "轉": ("{S}即將和{T}互換裝備", "{S} is about to swap equipment with {T}", "{S}が{T}と装備を入れ替えようとしています"),
    "降雷": ("{S}即將讓{T}翻面 (技能無法使用)", "{S} is about to flip {T} face-down (skills disabled)", "{S}が{T}を裏返そうとしています(スキル使用不可)"),
    "強": ("{S}即將讓{T}本回合造成的傷害 ×2", "{S} is about to double the damage {T} deals this turn", "{S}が{T}の今ターンのダメージを2倍にしようとしています"),
    "弱": ("{S}即將讓{T}本回合造成的傷害 ÷2", "{S} is about to halve the damage {T} deals this turn", "{S}が{T}の今ターンのダメージを半分にしようとしています"),
    "樂": ("{T}即將被判定樂不思蜀 (不是紅色就跳過出牌階段)", "{T} is about to be judged for Contentment (not red: skip the play phase)", "{T}が楽不思蜀の判定を受けます(赤以外: 出牌フェイズ飛ばし)"),
    "兵": ("{T}即將被判定兵糧寸斷 (不是黑色就跳過摸牌階段)", "{T} is about to be judged for Supply Shortage (not black: skip the draw phase)", "{T}が兵糧寸断の判定を受けます(黒以外: ドローフェイズ飛ばし)"),
    "閃電": ("{T}即將判定閃電 (黑色 −3 體力)", "{T} is about to judge Lightning (black: lose 3 HP)", "{T}が閃電の判定をします(黒: 体力-3)"),
    "毒": ("{T}即將判定毒 (紅色: 武將牌翻面)", "{T} is about to judge Poison (red: flip face-down)", "{T}が毒の判定をします(赤: 裏返し)"),
    "草": ("{T}即將判定草木皆兵 (不是黑色: 少摸 1 張)", "{T} is about to judge Paranoia (not black: draw 1 fewer)", "{T}が草木皆兵の判定をします(黒以外: ドロー-1)"),
}
# 群體錦囊: (效果, 英, 日);結尾另外帶「你在其中 / 你不在其中」
G = {
    "南": ("南蠻入侵: 其他玩家各出一張殺,否則 −1 體力", "Barbarians: every other player plays an Attack or loses 1 HP", "南蛮入侵: 他の全員が殺を出さないと体力-1"),
    "萬": ("萬箭齊發: 其他玩家各出一張閃,否則 −1 體力", "Arrow Barrage: every other player plays a Dodge or loses 1 HP", "万箭斉発: 他の全員が閃を出さないと体力-1"),
    "飢": ("飢餓: 其他玩家各出桃,否則 −1 體力", "Famine: every other player plays a Peach or loses 1 HP", "飢餓: 他の全員が桃を出さないと体力-1"),
    "突": ("突襲: 依序每人出殺,沒出的 −1 體力", "Raid: each player in turn plays an Attack or loses 1 HP", "突襲: 順番に殺を出さないと体力-1"),
}
IN, OUT = "你在其中", "你不在其中"
TAIL = ",要使用無懈嗎?"


def hint(g, p, ctx):
    """回傳摘要句 (結尾已含「要使用無懈嗎?」);不認得的牌回傳 None (用原本的提示)。"""
    try:
        trick, src, tgt = ctx.get("trick"), ctx.get("source"), ctx.get("target")
        targets = ctx.get("targets")
        S = label(g, p, src) if isinstance(src, Player) else ""
        if targets and trick in G:
            ins = IN if p in targets else OUT
            s = f"{S}即將使用{G[trick][0]} ({ins})"
        elif trick in T and (isinstance(tgt, Player) or "{T}" not in T[trick][0]):
            Tl = label(g, p, tgt) if isinstance(tgt, Player) else ""
            s = T[trick][0].replace("{S}", S).replace("{T}", Tl)
        else:
            return None
        s += TAIL
        if ctx.get("negated"):
            s = "已被無懈 — " + s
        return s
    except Exception:
        return None


def i18n_lines():
    """產生 web/i18n_ui.js 要的翻譯樣板 (SGS_LOG_TPL 格式)。"""
    out = []
    def add(zh, en, ja):
        out.append([zh, en, ja])
    for k, (zh, en, ja) in T.items():
        zz = zh
        order = []
        for ph in ("{S}", "{T}"):
            if ph in zz:
                order.append((zz.index(ph), ph))
        order.sort()
        idx = {ph: i + 1 for i, (_, ph) in enumerate(order)}
        def conv(t):
            for ph, i in idx.items():
                t = t.replace(ph, "{%d}" % i)
            return t
        zz2 = zz
        for ph in idx:
            zz2 = zz2.replace(ph, "{}")
        add(zz2 + TAIL, conv(en) + ". Use Nullify?", conv(ja) + "。無懈可撃を使いますか?")
    for k, (zh, en, ja) in G.items():
        for ins, ine, inj in ((IN, "you are included", "あなたも対象"), (OUT, "you are not included", "あなたは対象外")):
            add("{}即將使用" + zh + f" ({ins})" + TAIL, "{1} is about to use " + en + f" ({ine}). Use Nullify?", "{1}が" + ja + f"({inj})を使おうとしています。無懈可撃を使いますか?")
    add("已被無懈 — {}", "Already Nullified — {1}", "無懈済み — {1}")
    add("敵方{}", "Enemy {1}", "敵方 {1}")
    add("友方{}", "Ally {1}", "味方 {1}")
    add("身分不明的{}", "Unknown {1}", "身元不明の{1}")
    return out
