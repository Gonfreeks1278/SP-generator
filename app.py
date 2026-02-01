import streamlit as st
from openai import OpenAI
import base64
import json

# ===== Secrets =====
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

SALON_NAME = st.secrets["SALON_NAME"]
SALON_AREA = st.secrets["SALON_AREA"]
SALON_CONCEPT = st.secrets["SALON_CONCEPT"]
SALON_TARGET = st.secrets["SALON_TARGET"]
SALON_SERVICE = st.secrets["SALON_SERVICE"]

# ===== Page =====
st.set_page_config(page_title="SNS投稿ジェネレーター", layout="centered")

st.title("🌿 SNS投稿ジェネレーター")
st.caption("画像を入れるだけで、上品・自然派の投稿文を作成します")

# ===== UI =====
uploaded_file = st.file_uploader(
    "施術写真・動画をアップロードしてください",
    type=["png", "jpg", "jpeg", "mp4"]
)

post_type = st.selectbox(
    "投稿タイプ",
    ["施術紹介", "デザイン紹介", "空き状況・予約案内", "日常・想い"]
)

platforms = st.multiselect(
    "投稿先",
    ["Instagram", "X"],
    default=["Instagram"]
)

generate = st.button("✨ 投稿文を生成")

# ===== Prompt =====
SYSTEM_PROMPT = """
あなたは経験豊富なアイリストであり、
上品で自然派の世界観を大切にする美容サロンのSNS担当者です。

誇張表現・効果断定・医療表現は禁止。
やわらかく落ち着いた日本語で書いてください。
"""

USER_PROMPT = f"""
以下の画像をもとにSNS投稿文を作ってください。

サロン情報：
・地域：{SALON_AREA}
・コンセプト：{SALON_CONCEPT}
・サービス：{SALON_SERVICE}
・ターゲット：{SALON_TARGET}

投稿タイプ：{post_type}

【出力形式】
必ずJSON形式で出力してください。

{{
  "instagram": "Instagram用の本文（改行・ハッシュタグ含む）",
  "x": "X用の本文（140文字以内）"
}}

Instagram：
・3〜6行
・最後に自然な予約導線
・ハッシュタグ10〜15個
・#{SALON_NAME} を必ず含める

X：
・余白のある文章
・ハッシュタグ2〜3個
・#{SALON_NAME} を必ず含める
"""

# ===== Execute =====
if generate and uploaded_file:
    with st.spinner("生成中..."):
        image_bytes = uploaded_file.read()
        image_base64 = base64.b64encode(image_bytes).decode()

        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": USER_PROMPT},
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

    raw_text = res.choices[0].message.content

    try:
        json_start = raw_text.index("{")
        json_end = raw_text.rindex("}") + 1
        json_text = raw_text[json_start:json_end]
        data = json.loads(json_text)
    except Exception:
        st.error("生成結果の解析に失敗しました")
        st.text_area("デバッグ用：AIの生出力", raw_text, height=300)
        st.stop()

    st.success("生成完了！")

    if "Instagram" in platforms:
        st.subheader("📸 Instagram用")
        st.code(data["instagram"], language="text")
        st.caption("右上の📋でワンクリックコピー")

    if "X" in platforms:
        st.subheader("📝 X用")
        st.code(data["x"], language="text")

elif generate:
    st.warning("画像をアップロードしてください")
