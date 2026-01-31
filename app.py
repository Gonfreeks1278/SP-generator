import streamlit as st
from openai import OpenAI
import base64

# ===== Secrets 読み込み =====
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

SALON_NAME = st.secrets["SALON_NAME"]
SALON_AREA = st.secrets["SALON_AREA"]
SALON_CONCEPT = st.secrets["SALON_CONCEPT"]
SALON_TARGET = st.secrets["SALON_TARGET"]
SALON_SERVICE = st.secrets["SALON_SERVICE"]

# ===== ページ設定 =====
st.set_page_config(page_title="SNS投稿ジェネレーター", layout="centered")

st.title("🌿 SNS投稿ジェネレーター")
st.caption("画像を入れるだけで、上品・自然派の投稿文を作成します")

# ===== 入力UI =====
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
    default=["Instagram", "X"]
)

generate = st.button("✨ 投稿文を生成")

# ===== プロンプト =====
SYSTEM_PROMPT = """
あなたは経験豊富なアイリストであり、
上品で自然派の世界観を大切にする美容サロンのSNS担当者です。

以下を必ず守ってください。
・誇張表現や効果の断定はしない
・医療的・薬機法に抵触する表現は避ける
・煽り・強い売り込みはしない
・落ち着いた、やわらかい日本語を使う
・お客様目線で安心感を与える
・大人の女性向けのトーンにする

文章は「丁寧・上品・自然体」を最優先にしてください。
"""

USER_PROMPT_TEMPLATE = f"""
以下の画像（または動画）をもとに、
あなたは{SALON_AREA}で活動する
「{SALON_CONCEPT}」を大切にする
{SALON_SERVICE}の専門家です。

ターゲットは{SALON_TARGET}です。

この画像を使って、新規のお客様にも伝わる
上品で自然なSNS投稿文を作ってください。

【投稿条件】
・投稿先：{{platforms}}
・投稿タイプ：{{post_type}}
・トーン：上品・自然派

【出力形式】
▼Instagram用
・3〜6行程度
・やわらかく世界観を表現
・最後に自然な導線（予約・プロフィール誘導）
・ハッシュタグ10〜15個
  （業種＋地域＋ナチュラル系＋
   #{{SALON_NAME}} を必ず含める）

▼X用
・140文字以内
・余白のある文章
・ハッシュタグ2〜3個
  （#{{SALON_NAME}} を必ず含める）

【注意点】
・Before/Afterの効果を断定しない
・「改善した」「治る」などの表現は使わない
・見た目の印象や雰囲気にフォーカスする
"""

# ===== 実行 =====
if generate and uploaded_file:
    with st.spinner("投稿文を生成中..."):
        image_bytes = uploaded_file.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": USER_PROMPT_TEMPLATE.format(
                                platforms=", ".join(platforms),
                                post_type=post_type,
                                SALON_NAME=SALON_NAME
                            )
                        },
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

        st.success("生成完了！")

        st.text_area(
            "📄 生成された投稿文（そのままコピペOK）",
            response.choices[0].message.content,
            height=420
        )

elif generate:
    st.warning("画像または動画をアップロードしてください。")
