import streamlit as st
from openai import OpenAI
import base64
import random

# ===== Secrets =====
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

SALON_NAME = st.secrets["SALON_NAME"]
SALON_AREA = st.secrets["SALON_AREA"]
SALON_CONCEPT = st.secrets["SALON_CONCEPT"]

# ===== 初期state =====
if "last_content" not in st.session_state:
    st.session_state.last_content = None
if "last_variation" not in st.session_state:
    st.session_state.last_variation = None

# ===== ページ =====
st.set_page_config(page_title="SNS投稿ジェネレーター", layout="centered")
st.title("🌿 SNS投稿ジェネレーター")
st.caption("被ったら、ワンクリックで作り直せます")

# ===== UI =====
uploaded_file = st.file_uploader(
    "施術写真をアップロード",
    type=["png", "jpg", "jpeg"]
)

post_type = st.selectbox(
    "投稿タイプ",
    ["施術紹介", "デザイン紹介", "空き状況・予約案内", "日常・想い"]
)

st.markdown("### 👤 顧客属性")
age_group = st.multiselect(
    "年代",
    ["10代", "20代", "30代", "40代", "50代", "60代"]
)

gender = st.radio(
    "性別",
    ["女性", "男性", "指定しない"],
    horizontal=True
)

st.markdown("### 💄 メニュー")
menus = st.multiselect(
    "施術メニュー",
    [
        "コスメパーマ",
        "パリジェンヌ",
        "アイブロウ",
        "HBL",
        "フラットラッシュ",
        "ミンク",
        "フラットマットラッシュ"
    ]
)

st.markdown("### ✨ 施術ポイント")
points = st.multiselect(
    "今回のポイント",
    [
        "カール感",
        "立ち上がり",
        "横から見たライン",
        "目の縦幅",
        "メイクとの相性",
        "自まつげの活かし方",
        "骨格バランス"
    ]
)

platforms = st.multiselect(
    "投稿先",
    ["Instagram", "X"],
    default=["Instagram"]
)

generate = st.button("✨ 投稿文を生成")
regen = st.button("🌀 前回と同じニュアンス → 作り直す")

# ===== プロンプト補助 =====
VARIATIONS = [
    "仕上がりの雰囲気から書き出す",
    "施術中のこだわり視点で書く",
    "お客様の日常に寄り添う書き方",
    "目元の印象変化にフォーカス",
    "ナチュラルさを言葉で表現する"
]

def generate_post(force_new=False):
    image_bytes = uploaded_file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    if force_new and st.session_state.last_variation:
        choices = [v for v in VARIATIONS if v != st.session_state.last_variation]
        variation = random.choice(choices)
    else:
        variation = random.choice(VARIATIONS)

    st.session_state.last_variation = variation

    prompt = f"""
以下の画像をもとにSNS投稿文を作成してください。

【サロン】
・地域：{SALON_AREA}
・コンセプト：{SALON_CONCEPT}
・店名：{SALON_NAME}

【条件】
・投稿タイプ：{post_type}
・年代：{", ".join(age_group) if age_group else "幅広い年代"}
・性別：{gender}
・メニュー：{", ".join(menus)}
・施術ポイント：{", ".join(points)}
・文章の切り口：{variation}

【出力形式】
▼Instagram用
・3〜6行
・上品・自然
・最後にやさしい導線
・ハッシュタグ10〜15個（#{SALON_NAME} 必須）

▼X用
・140文字以内
・ハッシュタグ2〜3個（#{SALON_NAME} 必須）
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "同じ言い回しを避けてください。"},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=700
    )

    st.session_state.last_content = response.choices[0].message.content

# ===== 実行 =====
if uploaded_file and (generate or regen):
    with st.spinner("生成中..."):
        generate_post(force_new=regen)

if st.session_state.last_content:
    content = st.session_state.last_content

    if "Instagram" in platforms:
        st.markdown("## 📸 Instagram用")
        insta = content.split("▼X用")[0].replace("▼Instagram用", "").strip()
        st.code(insta)
        st.button("📋 Instagram用をコピー", on_click=lambda: st.session_state.update({"_copy": insta}))

    if "X" in platforms and "▼X用" in content:
        st.markdown("## 🐦 X用")
        xtext = content.split("▼X用")[1].strip()
        st.code(xtext)
        st.button("📋 X用をコピー", on_click=lambda: st.session_state.update({"_copy": xtext}))
