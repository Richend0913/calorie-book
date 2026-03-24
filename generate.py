"""
カロリーブック (Calorie Book) - Static Site Generator
Generates SEO-optimized food calorie pages for Japanese audience.
"""
import os, json, re, math
from datetime import datetime

SITE_URL = "https://richend0913.github.io/calorie-book"
ADSENSE = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6327505164684489" crossorigin="anonymous"></script>'
NOW = datetime.now().strftime("%Y-%m-%d")

# ─── Food Data ───────────────────────────────────────────────────────────
# Format: (name, slug, cal, protein, fat, carb, sugar, fiber, salt,
#          serving_name, serving_g, category, advice, related_slugs)

FOODS = [
    # ── ご飯・麺類 ──
    ("白米", "hakumai", 168, 2.5, 0.3, 37.1, 36.8, 0.3, 0.0,
     "茶碗1杯", 150, "ご飯・麺類",
     ["玄米に置き換えると食物繊維が約3倍に増えます", "よく噛んで食べることで満腹感を高められます", "冷やすとレジスタントスターチが増え、実質カロリーが下がります"],
     ["genmai", "okayu", "onigiri", "chahan"]),
    ("玄米", "genmai", 165, 2.8, 1.0, 35.6, 34.2, 1.4, 0.0,
     "茶碗1杯", 150, "ご飯・麺類",
     ["白米より食物繊維が豊富で血糖値の上昇が緩やかです", "ビタミンB群が豊富で代謝をサポートします", "よく噛む必要があるため自然と食べ過ぎ防止になります"],
     ["hakumai", "okayu", "onigiri"]),
    ("うどん（ゆで）", "udon", 105, 2.6, 0.4, 21.6, 21.4, 0.2, 0.3,
     "1玉", 250, "ご飯・麺類",
     ["つゆの塩分に注意。減塩つゆを選びましょう", "野菜や卵をトッピングして栄養バランスを改善できます", "消化が良いので体調不良時にもおすすめです"],
     ["soba", "ramen", "pasta"]),
    ("そば（ゆで）", "soba", 132, 4.8, 1.0, 26.0, 24.0, 2.0, 0.0,
     "1玉", 200, "ご飯・麺類",
     ["うどんより食物繊維・たんぱく質が豊富です", "ルチンが含まれ血管の健康に寄与します", "GI値が低く血糖値の上昇が緩やかです"],
     ["udon", "ramen", "pasta"]),
    ("ラーメン（醤油）", "ramen", 89, 5.5, 2.0, 13.0, 12.5, 0.5, 2.5,
     "1杯（スープ込み）", 600, "ご飯・麺類",
     ["スープを残すだけで約200kcal・塩分を大幅カットできます", "チャーシューを鶏むね肉に変えるとヘルシーに", "野菜トッピングを増やして食物繊維を補いましょう"],
     ["udon", "soba", "tsukemen"]),
    ("パスタ（ゆで）", "pasta", 149, 5.2, 0.9, 28.4, 28.0, 0.4, 0.0,
     "1人前", 250, "ご飯・麺類",
     ["トマトソースはクリームソースより低カロリーです", "全粒粉パスタに替えると食物繊維アップ", "野菜をたっぷり加えてかさ増しすると満足感が上がります"],
     ["udon", "soba", "ramen"]),
    ("食パン", "shokupan", 260, 9.3, 4.4, 46.7, 44.4, 2.3, 1.3,
     "6枚切り1枚", 60, "ご飯・麺類",
     ["バターやジャムのカロリーに注意しましょう", "全粒粉パンに替えると栄養価が上がります", "トーストにするとGI値がやや下がります"],
     ["hakumai", "genmai", "onigiri"]),
    ("おにぎり（鮭）", "onigiri", 179, 4.0, 1.2, 37.8, 37.5, 0.3, 0.8,
     "1個", 110, "ご飯・麺類",
     ["具材で栄養価が大きく変わります。鮭はたんぱく質が豊富", "コンビニおにぎりは塩分が多めなので注意", "冷たいおにぎりはレジスタントスターチが増えます"],
     ["hakumai", "genmai", "chahan"]),
    ("お粥", "okayu", 71, 1.1, 0.1, 15.8, 15.7, 0.1, 0.0,
     "1杯", 250, "ご飯・麺類",
     ["水分が多く低カロリーで満腹感が得られます", "ダイエット中の主食置き換えに最適です", "消化が良く胃腸に優しい食事です"],
     ["hakumai", "genmai", "onigiri"]),
    ("チャーハン", "chahan", 181, 5.8, 6.5, 25.0, 24.5, 0.5, 1.2,
     "1人前", 300, "ご飯・麺類",
     ["油の量を減らすだけで大幅にカロリーダウンできます", "卵と野菜を多めにすると栄養バランスが良くなります", "カリフラワーライスで置き換えると糖質オフに"],
     ["hakumai", "curry_rice", "gyudon"]),
    ("カレーライス", "curry_rice", 160, 4.5, 5.5, 24.0, 22.5, 1.5, 1.5,
     "1皿", 400, "ご飯・麺類",
     ["ご飯を半分にするだけでカロリー大幅カット", "野菜カレーにすると脂質を抑えられます", "ルーを少なめにしてスパイスで風味を出すと◎"],
     ["chahan", "gyudon", "oyakodon"]),
    ("牛丼", "gyudon", 152, 6.5, 5.8, 19.0, 18.0, 1.0, 1.4,
     "並盛1杯", 350, "ご飯・麺類",
     ["ご飯少なめ（ミニ盛り）を選ぶとカロリーカット", "紅生姜は塩分が高いので控えめに", "サラダセットを付けると血糖値の上昇を緩やかにできます"],
     ["oyakodon", "curry_rice", "chahan"]),
    ("親子丼", "oyakodon", 145, 7.8, 4.2, 19.5, 18.5, 1.0, 1.3,
     "1杯", 350, "ご飯・麺類",
     ["鶏肉と卵でたんぱく質が豊富な丼です", "つゆの量を控えめにすると塩分カットに", "ご飯を少なめにすると糖質オフできます"],
     ["gyudon", "curry_rice", "tori_mune"]),
    ("つけ麺", "tsukemen", 120, 5.0, 3.5, 17.0, 16.5, 0.5, 2.0,
     "1人前", 400, "ご飯・麺類",
     ["つけ汁を全部飲まないことでカロリーカット", "太麺はよく噛むため満腹感が得られやすいです", "野菜トッピングを追加して栄養バランスを"],
     ["ramen", "soba", "udon"]),

    # ── 肉類 ──
    ("鶏むね肉（皮なし）", "tori_mune", 108, 22.3, 1.5, 0.0, 0.0, 0.0, 0.1,
     "1枚", 250, "肉類",
     ["高たんぱく低脂質でダイエットの味方です", "パサつきが気になる場合はブライン液に漬けると◎", "サラダチキンとして手軽に摂取できます"],
     ["tori_momo", "buta_rosu", "sasami"]),
    ("鶏もも肉（皮付き）", "tori_momo", 200, 16.2, 14.0, 0.0, 0.0, 0.0, 0.2,
     "1枚", 300, "肉類",
     ["皮を取り除くだけでカロリー約30%カット", "焼く・蒸すなど油を使わない調理法がおすすめ", "ジューシーでたんぱく質も豊富な食材です"],
     ["tori_mune", "buta_bara", "buta_rosu"]),
    ("ささみ", "sasami", 105, 23.0, 0.8, 0.0, 0.0, 0.0, 0.1,
     "2本", 100, "肉類",
     ["最も低脂質な肉のひとつです", "筋トレ中のたんぱく質補給に最適", "蒸してほぐすとサラダに活用しやすいです"],
     ["tori_mune", "tori_momo", "maguro"]),
    ("豚バラ肉", "buta_bara", 386, 14.2, 34.6, 0.1, 0.1, 0.0, 0.1,
     "3枚", 100, "肉類",
     ["脂質が非常に高いので量に注意が必要です", "茹でこぼすと余分な脂が落ちます", "豚ロースに置き換えるとカロリー約半分に"],
     ["buta_rosu", "tori_momo", "gyu_kata_rosu"]),
    ("豚ロース", "buta_rosu", 263, 19.3, 19.2, 0.2, 0.2, 0.0, 0.1,
     "1枚", 120, "肉類",
     ["脂身を取り除くとさらにカロリーダウン", "トンカツにすると衣で+100kcal以上増えます", "生姜焼きなど薄切りにして量を調整しやすいです"],
     ["buta_bara", "tori_momo", "gyu_kata_rosu"]),
    ("牛肩ロース", "gyu_kata_rosu", 240, 17.9, 17.4, 0.1, 0.1, 0.0, 0.1,
     "1枚（ステーキ）", 200, "肉類",
     ["赤身部分を選ぶと脂質を抑えられます", "グリルやオーブン調理で余分な脂を落とせます", "適量のたんぱく質で筋肉の維持に貢献します"],
     ["buta_rosu", "buta_bara", "hikiniku"]),
    ("合いびき肉", "hikiniku", 259, 17.3, 19.5, 0.3, 0.3, 0.0, 0.1,
     "100g", 100, "肉類",
     ["鶏ひき肉に替えると大幅にカロリーダウン", "炒める際に出る脂をキッチンペーパーで吸うと◎", "豆腐を混ぜてかさ増しする方法もおすすめです"],
     ["tori_mune", "buta_rosu", "gyu_kata_rosu"]),
    ("ベーコン", "bacon", 405, 12.9, 39.1, 0.3, 0.3, 0.0, 2.0,
     "2枚", 40, "肉類",
     ["少量でもカロリー・塩分が高い食材です", "ハーフベーコンやターキーベーコンが代替品に", "カリカリに焼くと余分な脂が落ちます"],
     ["sausage", "buta_bara", "buta_rosu"]),
    ("ソーセージ", "sausage", 321, 11.5, 28.5, 3.0, 2.9, 0.1, 1.9,
     "2本", 60, "肉類",
     ["加工肉は塩分が高いので頻度を控えましょう", "魚肉ソーセージの方がカロリー・脂質が低いです", "茹でると油で焼くよりヘルシーです"],
     ["bacon", "buta_bara", "hikiniku"]),

    # ── 魚介類 ──
    ("サーモン（生）", "salmon", 204, 20.1, 12.4, 0.1, 0.1, 0.0, 0.1,
     "1切れ", 80, "魚介類",
     ["オメガ3脂肪酸が豊富で良質な脂です", "刺身で食べると調理による脂質追加がありません", "アスタキサンチンによる抗酸化作用も期待できます"],
     ["maguro", "saba", "ebi"]),
    ("マグロ（赤身）", "maguro", 125, 26.4, 1.4, 0.1, 0.1, 0.0, 0.1,
     "刺身5切れ", 80, "魚介類",
     ["赤身は高たんぱく低脂質でダイエット向き", "トロは脂質が多いので赤身を選びましょう", "鉄分も豊富で貧血予防にも役立ちます"],
     ["salmon", "saba", "ebi"]),
    ("サバ", "saba", 202, 20.7, 12.1, 0.3, 0.3, 0.0, 0.3,
     "1切れ", 80, "魚介類",
     ["DHAやEPAが豊富で脳の健康をサポート", "サバ缶は手軽にたんぱく質が摂れます", "味噌煮缶は塩分が高めなので水煮缶がおすすめ"],
     ["salmon", "maguro", "ebi"]),
    ("エビ", "ebi", 82, 18.4, 0.6, 0.3, 0.3, 0.0, 0.4,
     "5尾", 100, "魚介類",
     ["低カロリー高たんぱくでダイエットに最適", "コレステロールは高めですが食事性の影響は限定的", "天ぷら・フライにすると高カロリーになるので注意"],
     ["ika", "maguro", "salmon"]),
    ("イカ", "ika", 88, 18.1, 1.2, 0.2, 0.2, 0.0, 0.5,
     "1杯", 150, "魚介類",
     ["低脂質で高たんぱく質な優秀食材です", "タウリンが豊富で肝機能の改善に期待", "よく噛むため満腹感が得られやすいです"],
     ["ebi", "maguro", "salmon"]),

    # ── 野菜 ──
    ("キャベツ", "cabbage", 23, 1.3, 0.2, 5.2, 3.4, 1.8, 0.0,
     "葉2枚", 100, "野菜",
     ["食前にキャベツを食べると食べ過ぎ防止に", "ビタミンCやビタミンKが豊富です", "生でも加熱しても使える万能野菜です"],
     ["tomato", "kyuri", "broccoli"]),
    ("トマト", "tomato", 19, 0.7, 0.1, 4.7, 3.7, 1.0, 0.0,
     "中1個", 150, "野菜",
     ["リコピンが豊富で抗酸化作用があります", "加熱するとリコピンの吸収率がアップします", "ダイエット中の間食に最適な低カロリー食材"],
     ["cabbage", "kyuri", "ninjin"]),
    ("きゅうり", "kyuri", 14, 1.0, 0.1, 3.0, 1.9, 1.1, 0.0,
     "1本", 100, "野菜",
     ["ほぼ水分で構成されており超低カロリーです", "カリウムが含まれむくみ解消に効果的", "食感が良く満足感を得やすい食材です"],
     ["cabbage", "tomato", "ninjin"]),
    ("にんじん", "ninjin", 39, 0.7, 0.2, 9.3, 6.5, 2.8, 0.1,
     "中1本", 150, "野菜",
     ["βカロテンが豊富で免疫力向上に寄与", "油と一緒に摂るとβカロテンの吸収率アップ", "甘みがあるので自然な味付けに活用できます"],
     ["broccoli", "cabbage", "horenso"]),
    ("ブロッコリー", "broccoli", 33, 4.3, 0.5, 5.2, 0.8, 4.4, 0.1,
     "1/2株", 125, "野菜",
     ["野菜の中でもたんぱく質が豊富で筋トレ民に人気", "ビタミンCはレモンの約2倍含まれています", "茹ですぎると栄養が流出するので蒸し調理が◎"],
     ["horenso", "cabbage", "tomato"]),
    ("ほうれん草", "horenso", 20, 2.2, 0.4, 3.1, 0.3, 2.8, 0.0,
     "1/2束", 100, "野菜",
     ["鉄分が豊富で貧血予防に効果的です", "茹でるとシュウ酸が減り食べやすくなります", "低カロリーで栄養密度が非常に高い野菜です"],
     ["broccoli", "cabbage", "ninjin"]),
    ("玉ねぎ", "tamanegi", 37, 1.0, 0.1, 8.8, 7.2, 1.6, 0.0,
     "中1個", 200, "野菜",
     ["硫化アリルが血液サラサラ効果を持ちます", "加熱すると甘みが増しカロリーは変わりません", "料理のベースとして幅広く使える万能野菜です"],
     ["ninjin", "cabbage", "tomato"]),

    # ── 果物 ──
    ("りんご", "apple", 57, 0.2, 0.3, 15.5, 13.1, 2.4, 0.0,
     "中1個", 250, "果物",
     ["食物繊維（ペクチン）が腸内環境を改善します", "皮ごと食べると栄養価がアップします", "間食をりんごに置き換えるとカロリーカットに"],
     ["banana", "mikan", "ichigo"]),
    ("バナナ", "banana", 86, 1.1, 0.2, 22.5, 21.4, 1.1, 0.0,
     "1本", 120, "果物",
     ["即効性のエネルギー源で運動前におすすめ", "カリウムが豊富でむくみ解消効果あり", "1本約100kcalで手軽なおやつに最適"],
     ["apple", "mikan", "ichigo"]),
    ("みかん", "mikan", 46, 0.7, 0.1, 12.0, 10.0, 2.0, 0.0,
     "中2個", 150, "果物",
     ["ビタミンCが豊富で風邪予防に効果的", "食物繊維は薄皮ごと食べると多く摂れます", "低カロリーで甘みがあるので間食に最適"],
     ["apple", "banana", "ichigo"]),
    ("いちご", "ichigo", 34, 0.9, 0.1, 8.5, 7.1, 1.4, 0.0,
     "5粒", 75, "果物",
     ["ビタミンCが果物の中でトップクラスです", "低カロリーでダイエット中のデザートに◎", "練乳やチョコをつけるとカロリーが跳ね上がるので注意"],
     ["mikan", "apple", "budou"]),
    ("ぶどう", "budou", 59, 0.4, 0.1, 15.7, 15.2, 0.5, 0.0,
     "1房", 150, "果物",
     ["ポリフェノールが豊富で抗酸化作用があります", "糖質が高めなので食べ過ぎに注意", "皮ごと食べられる品種を選ぶと栄養価アップ"],
     ["apple", "banana", "mikan"]),

    # ── お菓子・スイーツ ──
    ("ショートケーキ", "shortcake", 344, 5.5, 17.2, 43.0, 41.5, 1.5, 0.2,
     "1切れ", 110, "お菓子・スイーツ",
     ["1切れで約380kcal。週1回程度に抑えましょう", "生クリームの量でカロリーが大きく変動します", "フルーツ多めのケーキを選ぶと若干ヘルシーに"],
     ["chocolate", "icecream", "potechips"]),
    ("チョコレート（ミルク）", "chocolate", 558, 6.9, 34.1, 55.8, 51.9, 3.9, 0.1,
     "板チョコ1枚", 50, "お菓子・スイーツ",
     ["高カカオチョコ（70%以上）に替えると糖質カット", "1日20g程度なら健康効果も期待できます", "食べるなら午後3時頃が体脂肪になりにくい時間帯"],
     ["shortcake", "icecream", "potechips"]),
    ("ポテトチップス", "potechips", 554, 4.7, 35.2, 54.7, 53.0, 1.7, 1.0,
     "1袋", 60, "お菓子・スイーツ",
     ["1袋で約330kcal。小袋サイズを選びましょう", "ノンフライ製法を選ぶとカロリーダウン", "代替としてポップコーン（ノンオイル）がおすすめ"],
     ["chocolate", "shortcake", "icecream"]),
    ("アイスクリーム（バニラ）", "icecream", 207, 3.5, 12.0, 23.2, 23.0, 0.2, 0.1,
     "1カップ", 150, "お菓子・スイーツ",
     ["氷菓やシャーベットに替えるとカロリー半減", "ラクトアイスよりアイスクリームの方が乳脂肪で満足感", "食後のデザートより午後の間食として楽しむのが◎"],
     ["shortcake", "chocolate", "potechips"]),
    ("大福もち", "daifuku", 242, 4.5, 0.4, 53.8, 50.0, 3.8, 0.0,
     "1個", 80, "お菓子・スイーツ",
     ["和菓子は洋菓子より脂質が低い傾向です", "1個約190kcalなので1個に抑えましょう", "豆大福は食物繊維が豊富でおすすめです"],
     ["shortcake", "chocolate", "icecream"]),
    ("せんべい", "senbei", 373, 7.2, 1.0, 83.0, 82.0, 1.0, 1.5,
     "2枚", 30, "お菓子・スイーツ",
     ["脂質は低いですが糖質・塩分は高めです", "ノンフライで洋菓子よりヘルシーな間食", "食べ過ぎに注意し2〜3枚で止めましょう"],
     ["potechips", "daifuku", "chocolate"]),

    # ── 飲み物 ──
    ("ビール", "beer", 40, 0.3, 0.0, 3.1, 3.1, 0.0, 0.0,
     "中ジョッキ1杯", 500, "飲み物",
     ["1杯約200kcal。おつまみのカロリーも要注意", "糖質ゼロビールに替えると糖質カットできます", "アルコールは代謝を低下させるため飲み過ぎ注意"],
     ["nihonshu", "cola", "gyunyu"]),
    ("日本酒", "nihonshu", 103, 0.4, 0.0, 3.6, 3.6, 0.0, 0.0,
     "1合", 180, "飲み物",
     ["1合で約185kcal。糖質もビールより高めです", "熱燗にすると飲むペースが落ちて飲み過ぎ防止に", "和らぎ水（チェイサー）を挟みながら飲みましょう"],
     ["beer", "cola", "gyunyu"]),
    ("コーラ", "cola", 46, 0.0, 0.0, 11.3, 11.3, 0.0, 0.0,
     "1缶", 350, "飲み物",
     ["1缶で約160kcal・糖質40g。角砂糖約10個分です", "ゼロカロリーコーラに替えると糖質ゼロに", "水やお茶に置き換えるのが最も効果的です"],
     ["beer", "gyunyu", "tonyu"]),
    ("牛乳", "gyunyu", 61, 3.3, 3.8, 4.8, 4.8, 0.0, 0.1,
     "コップ1杯", 200, "飲み物",
     ["カルシウムが豊富で骨の健康に不可欠", "低脂肪牛乳に替えるとカロリー約30%カット", "運動後のたんぱく質補給にも効果的です"],
     ["tonyu", "cola", "beer"]),
    ("豆乳（無調整）", "tonyu", 46, 3.6, 2.0, 3.1, 2.5, 0.6, 0.0,
     "コップ1杯", 200, "飲み物",
     ["牛乳より低カロリーで植物性たんぱく質が豊富", "イソフラボンが女性ホルモンに似た働きをします", "調整豆乳は砂糖入りなので無調整を選びましょう"],
     ["gyunyu", "cola", "beer"]),
    ("緑茶", "greentea", 2, 0.2, 0.0, 0.2, 0.0, 0.2, 0.0,
     "湯呑み1杯", 150, "飲み物",
     ["ほぼゼロカロリーで水分補給に最適", "カテキンが脂肪燃焼をサポートします", "食事中に飲むと脂肪の吸収を抑える効果も"],
     ["gyunyu", "tonyu", "cola"]),
    ("オレンジジュース", "orange_juice", 42, 0.7, 0.1, 10.7, 10.0, 0.7, 0.0,
     "コップ1杯", 200, "飲み物",
     ["ビタミンCは豊富ですが糖質も高めです", "100%果汁でも飲み過ぎには注意しましょう", "果物をそのまま食べる方が食物繊維も摂れます"],
     ["cola", "gyunyu", "tonyu"]),

    # ── 外食メニュー ──
    ("ビッグマック", "bigmac", 241, 12.5, 13.0, 19.0, 17.5, 1.5, 1.3,
     "1個", 215, "外食メニュー",
     ["1個で約520kcal。セットにするとさらに倍近くに", "サイドをサラダに変えるとカロリーダウン", "ドリンクは水かお茶を選びましょう"],
     ["yoshinoya_gyudon", "sukiya_gyudon", "karaage_teishoku"]),
    ("吉野家 牛丼（並）", "yoshinoya_gyudon", 162, 7.5, 6.5, 19.5, 18.5, 1.0, 1.5,
     "並盛1杯", 380, "外食メニュー",
     ["ライザップ牛サラダなど低糖質メニューもあります", "つゆだく注文は塩分が増えるので注意", "サラダセットで野菜をプラスしましょう"],
     ["sukiya_gyudon", "gyudon", "bigmac"]),
    ("すき家 牛丼（並）", "sukiya_gyudon", 158, 7.2, 6.0, 19.8, 18.8, 1.0, 1.4,
     "並盛1杯", 380, "外食メニュー",
     ["ミニサイズを選ぶとカロリーを約3割カット", "牛丼ライトは豆腐に置き換えで糖質大幅オフ", "サラダセットを追加して食物繊維を補いましょう"],
     ["yoshinoya_gyudon", "gyudon", "bigmac"]),
    ("唐揚げ定食", "karaage_teishoku", 175, 13.0, 9.5, 12.0, 11.0, 1.0, 1.2,
     "1人前", 450, "外食メニュー",
     ["揚げ物は衣が油を吸ってカロリー高め", "レモンを絞ると脂肪の吸収を抑える効果あり", "ご飯を少なめにして全体カロリーを調整しましょう"],
     ["bigmac", "yoshinoya_gyudon", "tori_momo"]),
    ("天ぷらうどん", "tempura_udon", 105, 4.5, 2.5, 17.0, 16.5, 0.5, 2.5,
     "1杯", 500, "外食メニュー",
     ["天ぷらが1つ増えるごとに約80kcal追加", "かけうどんにすると約350kcalまで下がります", "つゆを飲み干さないことで塩分カット"],
     ["udon", "soba", "ramen"]),
    ("ざるそば", "zarusoba", 132, 5.0, 1.0, 26.0, 24.0, 2.0, 1.5,
     "1人前", 250, "外食メニュー",
     ["シンプルで比較的低カロリーな外食メニュー", "そば湯でビタミンB群を無駄なく摂取", "大盛りにすると一気にカロリーが増えるので注意"],
     ["soba", "udon", "tempura_udon"]),

    # ── 卵・乳製品 ──
    ("卵（鶏卵）", "tamago", 151, 12.3, 10.3, 0.3, 0.3, 0.0, 0.4,
     "1個", 60, "卵・乳製品",
     ["完全栄養食と呼ばれるほど栄養バランスが良い", "1日2〜3個程度は健康的に摂取できます", "ゆで卵は調理油不要で最もヘルシーな食べ方"],
     ["gyunyu", "cheese", "tori_mune"]),
    ("プロセスチーズ", "cheese", 339, 22.7, 26.0, 1.3, 1.3, 0.0, 2.8,
     "1切れ", 20, "卵・乳製品",
     ["少量でたんぱく質とカルシウムが摂れます", "塩分が高いので量に注意しましょう", "カッテージチーズに替えると脂質大幅カット"],
     ["tamago", "gyunyu", "tonyu"]),
    ("ヨーグルト（プレーン）", "yogurt", 62, 3.6, 3.0, 4.9, 4.9, 0.0, 0.1,
     "1カップ", 100, "卵・乳製品",
     ["乳酸菌が腸内環境を改善します", "無糖タイプを選んで果物を加えるのがおすすめ", "朝食に摂ると腸が活性化されやすいです"],
     ["gyunyu", "tonyu", "tamago"]),

    # ── 豆類・大豆製品 ──
    ("豆腐（絹ごし）", "tofu", 56, 4.9, 3.0, 2.0, 1.7, 0.3, 0.0,
     "1/2丁", 150, "豆類・大豆製品",
     ["低カロリー高たんぱくでダイエットの強い味方", "主食の置き換えとして使うと糖質オフに", "イソフラボンが美容と健康をサポートします"],
     ["natto", "tonyu", "tamago"]),
    ("納豆", "natto", 200, 16.5, 10.0, 12.1, 5.4, 6.7, 0.0,
     "1パック", 45, "豆類・大豆製品",
     ["発酵食品で腸内環境を整えてくれます", "ナットウキナーゼが血液サラサラ効果を発揮", "1日1パックを目安に摂取するのがおすすめ"],
     ["tofu", "tonyu", "tamago"]),

    # 追加の人気食品
    ("枝豆", "edamame", 135, 11.7, 6.2, 8.8, 3.8, 5.0, 0.0,
     "1皿", 100, "野菜",
     ["高たんぱくで低糖質。お酒のおつまみに最適", "大豆イソフラボンやビタミンKが豊富", "塩のかけすぎには注意しましょう"],
     ["tofu", "natto", "broccoli"]),
    ("アボカド", "avocado", 187, 2.5, 18.7, 6.2, 0.9, 5.3, 0.0,
     "1個", 140, "果物",
     ["脂質は高いですがオレイン酸など良質な脂肪酸", "食物繊維が豊富で満腹感が持続します", "1日半個程度が適量です"],
     ["banana", "apple", "broccoli"]),
    ("さつまいも", "satsumaimo", 134, 1.2, 0.2, 31.5, 29.2, 2.3, 0.0,
     "中1本", 200, "野菜",
     ["食物繊維が豊富で腸内環境を整えます", "GI値は白米より低く血糖値が上がりにくい", "焼き芋にすると甘みが増し満足感アップ"],
     ["hakumai", "banana", "ninjin"]),
    ("餃子", "gyoza", 197, 8.5, 9.8, 19.5, 18.5, 1.0, 1.5,
     "6個", 180, "外食メニュー",
     ["焼き餃子より水餃子の方が脂質控えめ", "野菜をたっぷり入れた手作りがおすすめ", "タレの酢の割合を増やすとさっぱりヘルシーに"],
     ["karaage_teishoku", "chahan", "ramen"]),
    ("カツ丼", "katsudon", 182, 8.5, 7.2, 22.0, 20.5, 1.5, 1.8,
     "1杯", 400, "外食メニュー",
     ["1杯で約730kcalと高カロリーメニュー", "ロースよりヒレカツを選ぶと脂質カット", "ご飯少なめにしてサラダを追加しましょう"],
     ["gyudon", "oyakodon", "karaage_teishoku"]),
    ("味噌汁", "misoshiru", 21, 1.3, 0.4, 3.0, 2.5, 0.5, 1.2,
     "1杯", 180, "外食メニュー",
     ["具だくさんにすると食事の満足度アップ", "塩分が気になる場合は減塩味噌を使いましょう", "わかめや豆腐を入れると栄養バランスが良くなります"],
     ["tofu", "natto", "udon"]),
]


def slug_to_filename(slug):
    return f"{slug}.html"


def make_bar_html(label, value, max_val, css_class, unit="g"):
    pct = min(value / max_val * 100, 100) if max_val > 0 else 0
    return f'''<div class="bar-item">
  <div class="bar-label"><span>{label}</span><span>{value}{unit}</span></div>
  <div class="bar-track"><div class="bar-fill {css_class}" style="width:{pct:.1f}%"></div></div>
</div>'''


def generate_food_page(food, all_foods):
    (name, slug, cal, protein, fat, carb, sugar, fiber, salt,
     serving_name, serving_g, category, advice, related_slugs) = food

    s_cal = round(cal * serving_g / 100)
    s_protein = round(protein * serving_g / 100, 1)
    s_fat = round(fat * serving_g / 100, 1)
    s_carb = round(carb * serving_g / 100, 1)
    s_sugar = round(sugar * serving_g / 100, 1)
    s_fiber = round(fiber * serving_g / 100, 1)
    s_salt = round(salt * serving_g / 100, 1)

    # Find related foods
    related_foods = [f for f in all_foods if f[1] in related_slugs]
    # Find same-category foods for comparison
    same_cat = [f for f in all_foods if f[11] == category and f[1] != slug][:5]

    # Bar chart max values (daily reference)
    cal_max = 300
    nutrient_max = 50

    bars_100g = (
        make_bar_html("カロリー", cal, cal_max, "cal", "kcal") +
        make_bar_html("たんぱく質", protein, nutrient_max, "protein") +
        make_bar_html("脂質", fat, nutrient_max, "fat") +
        make_bar_html("炭水化物", carb, nutrient_max * 2, "carb") +
        make_bar_html("糖質", sugar, nutrient_max * 2, "sugar") +
        make_bar_html("食物繊維", fiber, 10, "fiber") +
        make_bar_html("塩分", salt, 3, "salt")
    )

    bars_serving = (
        make_bar_html("カロリー", s_cal, 700, "cal", "kcal") +
        make_bar_html("たんぱく質", s_protein, nutrient_max, "protein") +
        make_bar_html("脂質", s_fat, nutrient_max, "fat") +
        make_bar_html("炭水化物", s_carb, nutrient_max * 2, "carb") +
        make_bar_html("糖質", s_sugar, nutrient_max * 2, "sugar") +
        make_bar_html("食物繊維", s_fiber, 10, "fiber") +
        make_bar_html("塩分", s_salt, 3, "salt")
    )

    advice_html = "\n".join(f"<li>{a}</li>" for a in advice)

    comparison_rows = f'''<tr class="current-row">
<td>{name}</td><td>{cal}</td><td>{protein}</td><td>{fat}</td><td>{carb}</td><td>{sugar}</td>
</tr>'''
    for f in same_cat:
        comparison_rows += f'''<tr>
<td><a href="{slug_to_filename(f[1])}">{f[0]}</a></td><td>{f[2]}</td><td>{f[3]}</td><td>{f[4]}</td><td>{f[5]}</td><td>{f[6]}</td>
</tr>'''

    related_html = "\n".join(
        f'<a href="{slug_to_filename(f[1])}" class="related-link">{f[0]}のカロリー</a>'
        for f in related_foods
    )

    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "NutritionInformation",
        "name": f"{name}の栄養成分",
        "calories": f"{cal} kcal",
        "proteinContent": f"{protein} g",
        "fatContent": f"{fat} g",
        "carbohydrateContent": f"{carb} g",
        "sugarContent": f"{sugar} g",
        "fiberContent": f"{fiber} g",
        "sodiumContent": f"{salt} g",
        "servingSize": f"{serving_name}（{serving_g}g）"
    }, ensure_ascii=False)

    faq_jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f"{name}のカロリーは？",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f"{name}は100gあたり{cal}kcalです。{serving_name}（{serving_g}g）あたりでは{s_cal}kcalになります。"
                }
            },
            {
                "@type": "Question",
                "name": f"{name}の糖質は？",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f"{name}の糖質は100gあたり{sugar}gです。{serving_name}（{serving_g}g）あたりでは{s_sugar}gになります。"
                }
            },
            {
                "@type": "Question",
                "name": f"{name}はダイエットに向いている？",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": advice[0] if advice else ""
                }
            }
        ]
    }, ensure_ascii=False)

    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name}のカロリー・糖質・栄養成分 | カロリーブック</title>
<meta name="description" content="{name}のカロリーは100gあたり{cal}kcal、{serving_name}（{serving_g}g）あたり{s_cal}kcal。たんぱく質{protein}g、脂質{fat}g、糖質{sugar}g。ダイエットに役立つ栄養情報を掲載。">
<meta name="keywords" content="{name} カロリー,{name} 糖質,{name} 栄養,{name} ダイエット,{name} たんぱく質">
<link rel="canonical" href="{SITE_URL}/foods/{slug_to_filename(slug)}">
<link rel="stylesheet" href="../css/style.css">
{ADSENSE}
<script type="application/ld+json">{jsonld}</script>
<script type="application/ld+json">{faq_jsonld}</script>
</head>
<body>

<header>
<div class="container">
<h1><a href="../index.html">カロリーブック</a></h1>
<nav>
<a href="../index.html">食品一覧</a>
</nav>
</div>
</header>

<div class="food-header">
<div class="container">
<span class="category-tag">{category}</span>
<h1>{name}のカロリー・栄養成分</h1>
<div class="calorie-big">{cal}<small> kcal</small></div>
<div class="per-note">100gあたり</div>
</div>
</div>

<div class="container">

<div class="breadcrumb">
<a href="../index.html">トップ</a><span>&gt;</span>
<a href="../index.html#{category}">{category}</a><span>&gt;</span>
{name}
</div>

<div class="ad-space">
<ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-6327505164684489" data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
</div>

<div class="nutrition-grid">
<div class="nutrition-card">
<h3>100gあたりの栄養成分</h3>
<div class="bar-chart">{bars_100g}</div>
</div>
<div class="nutrition-card">
<h3>{serving_name}（{serving_g}g）あたり</h3>
<div class="bar-chart">{bars_serving}</div>
</div>
</div>

<div class="nutrition-card">
<h3>栄養成分表</h3>
<table class="nutrition-table">
<tr><th>栄養素</th><th>100gあたり</th><th>{serving_name}（{serving_g}g）</th></tr>
<tr class="highlight"><td>エネルギー</td><td>{cal} kcal</td><td>{s_cal} kcal</td></tr>
<tr><td>たんぱく質</td><td>{protein} g</td><td>{s_protein} g</td></tr>
<tr><td>脂質</td><td>{fat} g</td><td>{s_fat} g</td></tr>
<tr><td>炭水化物</td><td>{carb} g</td><td>{s_carb} g</td></tr>
<tr class="highlight"><td>糖質</td><td>{sugar} g</td><td>{s_sugar} g</td></tr>
<tr><td>食物繊維</td><td>{fiber} g</td><td>{s_fiber} g</td></tr>
<tr><td>塩分相当量</td><td>{salt} g</td><td>{s_salt} g</td></tr>
</table>
</div>

<div class="ad-space">
<ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-6327505164684489" data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
</div>

<div class="advice-section">
<h3>{name}のダイエットアドバイス</h3>
<ul>{advice_html}</ul>
</div>

<div class="comparison-section">
<h3>{category}のカロリー比較（100gあたり）</h3>
<table class="comparison-table">
<tr><th>食品名</th><th>カロリー</th><th>たんぱく質</th><th>脂質</th><th>炭水化物</th><th>糖質</th></tr>
{comparison_rows}
</table>
</div>

<div class="ad-space">
<ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-6327505164684489" data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
</div>

<div class="related-section">
<h3>関連する食品のカロリー</h3>
<div class="related-links">
{related_html}
</div>
</div>

</div>

<footer>
<div class="container">
<p>&copy; {datetime.now().year} カロリーブック - 食品のカロリー・栄養成分データベース</p>
<p><a href="../index.html">トップページ</a></p>
</div>
</footer>

</body>
</html>'''
    return html


def generate_index(all_foods):
    categories = {}
    for food in all_foods:
        cat = food[11]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(food)

    cat_order = ["ご飯・麺類", "肉類", "魚介類", "野菜", "果物", "卵・乳製品",
                 "豆類・大豆製品", "お菓子・スイーツ", "飲み物", "外食メニュー"]

    sections = ""
    nav_links = ""
    for cat in cat_order:
        if cat not in categories:
            continue
        nav_links += f'<a href="#{cat}">{cat}</a>'
        cards = ""
        for f in categories[cat]:
            name, slug, cal, protein, fat, carb, sugar, fiber, salt, sname, sg, *_ = f
            s_cal = round(cal * sg / 100)
            cards += f'''<div class="food-card">
<h3><a href="foods/{slug_to_filename(slug)}">{name}</a></h3>
<span class="cal-badge">{cal} kcal/100g</span>
<div class="serving-info">{sname}（{sg}g）: {s_cal} kcal</div>
</div>
'''
        sections += f'''<div class="category-section" id="{cat}">
<h2>{cat}</h2>
<div class="food-grid">{cards}</div>
</div>
'''

    # Collect all food names for keywords
    all_names = ", ".join(f[0] for f in all_foods[:20])

    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "カロリーブック",
        "url": SITE_URL,
        "description": "食品のカロリー・糖質・栄養成分を簡単検索。ダイエットや健康管理に役立つ栄養情報データベース。",
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{SITE_URL}/foods/{{search_term_string}}.html",
            "query-input": "required name=search_term_string"
        }
    }, ensure_ascii=False)

    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>カロリーブック - 食品のカロリー・糖質・栄養成分データベース</title>
<meta name="description" content="食品のカロリー・糖質・栄養成分を簡単検索。{len(all_foods)}種類以上の食品データを掲載。ダイエットや健康管理に役立つ栄養情報データベース。">
<meta name="keywords" content="カロリー,糖質,栄養成分,ダイエット,食品カロリー,{all_names}">
<link rel="canonical" href="{SITE_URL}/">
<link rel="stylesheet" href="css/style.css">
{ADSENSE}
<script type="application/ld+json">{jsonld}</script>
</head>
<body>

<header>
<div class="container">
<h1><a href="index.html">カロリーブック</a></h1>
<nav>{nav_links}</nav>
</div>
</header>

<div class="hero">
<h2>食品のカロリー・栄養成分データベース</h2>
<p>{len(all_foods)}種類以上の食品のカロリー・糖質・たんぱく質・脂質などの栄養成分を掲載。ダイエットや健康管理にお役立てください。</p>
</div>

<div class="container">

<div class="ad-space">
<ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-6327505164684489" data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
</div>

{sections}

<div class="ad-space">
<ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-6327505164684489" data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
</div>

</div>

<footer>
<div class="container">
<p>&copy; {datetime.now().year} カロリーブック - 食品のカロリー・栄養成分データベース</p>
</div>
</footer>

</body>
</html>'''
    return html


def generate_sitemap(all_foods):
    urls = [f"  <url><loc>{SITE_URL}/</loc><lastmod>{NOW}</lastmod><priority>1.0</priority></url>"]
    for food in all_foods:
        urls.append(f"  <url><loc>{SITE_URL}/foods/{slug_to_filename(food[1])}</loc><lastmod>{NOW}</lastmod><priority>0.8</priority></url>")
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>'''


def generate_robots():
    return f'''User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
'''


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    foods_dir = os.path.join(base, "foods")
    os.makedirs(foods_dir, exist_ok=True)

    print(f"Generating {len(FOODS)} food pages...")

    for food in FOODS:
        html = generate_food_page(food, FOODS)
        path = os.path.join(foods_dir, slug_to_filename(food[1]))
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  Created: foods/{slug_to_filename(food[1])} ({food[0]})")

    index_html = generate_index(FOODS)
    with open(os.path.join(base, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)
    print("  Created: index.html")

    sitemap = generate_sitemap(FOODS)
    with open(os.path.join(base, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)
    print("  Created: sitemap.xml")

    robots = generate_robots()
    with open(os.path.join(base, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)
    print("  Created: robots.txt")

    print(f"\nDone! Generated {len(FOODS)} food pages + index + sitemap + robots.txt")


if __name__ == "__main__":
    main()
