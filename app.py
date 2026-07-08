import streamlit as st
import pandas as pd
import re
import json
from datetime import datetime, timedelta
import random

# ------------------------------------------------------------------
# ページ設定 & スタイル
# ------------------------------------------------------------------
st.set_page_config(
    page_title="FlashMaster - 高機能暗記カード",
    page_icon="🎴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSSの適用
st.markdown("""
<style>
    .main-title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        color: #4F46E5;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        color: #64748B;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .flashcard-box {
        background-color: #F8FAFC;
        border: 2px solid #E2E8F0;
        border-radius: 16px;
        padding: 3rem;
        text-align: center;
        min-height: 250px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    .flashcard-text {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1E293B;
    }
    .flashcard-back {
        background-color: #EEF2FF;
        border-color: #C7D2FE;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# セッション状態 (Session State) の初期化
# ------------------------------------------------------------------
if 'decks' not in st.session_state:
    st.session_state.decks = [
        {
            "id": "deck-1",
            "name": "英語頻出単語（最重要ボキャブラリー）",
            "description": "日常会話やビジネスで頻出する、最重要英単語の基礎カードセット。",
            "createdAt": "2026-07-01T09:00:00Z"
        },
        {
            "id": "deck-2",
            "name": "ウェブ開発基礎（フロントエンド）",
            "description": "React、TypeScript、ブラウザAPIなどの最新ウェブフロントエンド知識。",
            "createdAt": "2026-07-02T10:00:00Z"
        },
        {
            "id": "deck-3",
            "name": "世界史重要キーワード（世界史B）",
            "description": "歴史の流れを掴むための重要年号と歴史的出来事。",
            "createdAt": "2026-07-03T11:00:00Z"
        }
    ]

if 'cards' not in st.session_state:
    st.session_state.cards = [
        {"id": "card-1-1", "deckId": "deck-1", "front": "procrastinate", "back": "先延ばしにする、後回しにする（行動を遅らせたり、延期したりすること。）", "importance": 5, "createdAt": "2026-07-01T09:05:00Z"},
        {"id": "card-1-2", "deckId": "deck-1", "front": "resilient", "back": "回復力がある、立ち直りが早い（困難な状況から素早く立ち直る、回復力のある。）", "importance": 4, "createdAt": "2026-07-01T09:10:00Z"},
        {"id": "card-1-3", "deckId": "deck-1", "front": "conspicuous", "back": "人目を引く、目立つ（はっきりと見えて目立つ、人目を引く。）", "importance": 3, "createdAt": "2026-07-01T09:15:00Z"},
        {"id": "card-1-4", "deckId": "deck-1", "front": "ambiguous", "back": "曖昧な、二通りの解釈ができる（複数の解釈が可能で、意味が曖昧な。）", "importance": 4, "createdAt": "2026-07-01T09:20:00Z"},
        {"id": "card-1-5", "deckId": "deck-1", "front": "exquisite", "back": "非常に美しい、優雅な（この上なく美しく、極めて精巧な。）", "importance": 2, "createdAt": "2026-07-01T09:25:00Z"},
        {"id": "card-2-1", "deckId": "deck-2", "front": "Virtual DOM", "back": "状態変更時にメモリ上の仮想的なDOMツリー同士を比較し、差分のみを実際のDOMに高速に適用するReactの仕組み。", "importance": 5, "createdAt": "2026-07-02T10:05:00Z"},
        {"id": "card-2-2", "deckId": "deck-2", "front": "Generics", "back": "TypeScriptにおいて、型をパラメータ（引数）として扱い、再利用性の高いクラスや関数を作る仕組み。", "importance": 4, "createdAt": "2026-07-02T10:10:00Z"},
        {"id": "card-3-1", "deckId": "deck-3", "front": "パクス・ロマーナ", "back": "紀元前27年頃から約200年間続いた、ローマ帝国における「ローマの平和」と呼ばれる黄金期。", "importance": 4, "createdAt": "2026-07-03T11:05:00Z"}
    ]

if 'sessions' not in st.session_state:
    st.session_state.sessions = [
        {"id": "sess-1", "deckId": "deck-1", "deckName": "英語頻出単語", "date": "2026-07-03", "totalCards": 5, "score": 3},
        {"id": "sess-2", "deckId": "deck-1", "deckName": "英語頻出単語", "date": "2026-07-04", "totalCards": 5, "score": 4},
        {"id": "sess-3", "deckId": "deck-2", "deckName": "ウェブ開発基礎", "date": "2026-07-05", "totalCards": 4, "score": 2}
    ]

if 'weak_cards' not in st.session_state:
    st.session_state.weak_cards = [
        {"cardId": "card-1-2", "front": "resilient", "incorrectCount": 2}
    ]

# 学習・テスト中のステート
if 'study_index' not in st.session_state:
    st.session_state.study_index = 0
if 'study_flipped' not in st.session_state:
    st.session_state.study_flipped = False
if 'test_answers' not in st.session_state:
    st.session_state.test_answers = []
if 'test_shuffled_cards' not in st.session_state:
    st.session_state.test_shuffled_cards = []
if 'test_options' not in st.session_state:
    st.session_state.test_options = []

# ------------------------------------------------------------------
# 柔軟なインポート自動解析エンジン (Custom, CSV, Markdown)
# ------------------------------------------------------------------
def parse_imported_text(text, target_deck_id):
    parsed_cards = []
    
    # 1. 【カードNO. X】または「■表」「■裏」等のカスタム形式の判定
    has_card_no = bool(re.search(r'【カード(?:NO|No|no)?\.?\s*\d*\s*】', text))
    has_omote_ura = '■表' in text or '■裏' in text or '表（問題）' in text or '裏（解答）' in text
    
    if has_card_no or has_omote_ura:
        if has_card_no:
            chunks = re.split(r'【カード(?:NO|No|no)?\.?\s*\d*\s*】', text)
        else:
            chunks = re.split(r'(?=■表（問題）：|■表\(問題\)：|■表：|■表|表（問題）：|表\(問題\)：|表：|■問題)', text)
            
        start_front_keys = ['■表（問題）：', '■表(問題)：', '■表（問題）:', '■表(問題):', '■表：', '■表:', '■問題：', '■問題:', '表（問題）：', '表(問題)：', '表：', '表:']
        end_front_keys = ['■裏（解答・解説）：', '■裏(解答・解説)：', '■裏（解答・解説）:', '■裏(解答・解説):', '■裏：', '■裏:', '裏（解答・解説）：', '裏(解答・解説）：', '■裏（解答）:', '■裏(解答):', '■解答：', '■解答:', '■重要度：', '■重要度:', '重要度：', '重要度:']
        start_back_keys = ['■裏（解答・解説）：', '■裏(解答・解説)：', '■裏（解答・解説）:', '■裏(解答・解説):', '■裏：', '■裏:', '裏（解答・解説）：', '裏(解答・解説）：', '■裏（解答）:', '■裏(解答):', '■解答：', '■解答:', '裏：', '裏:']
        end_back_keys = ['■重要度：', '■重要度:', '重要度：', '重要度:', '【カード', '■表', '表（問題）', '■問題']
        
        def extract_value(content, start_keys, end_keys):
            best_start = -1
            for key in start_keys:
                idx = content.find(key)
                if idx != -1 and (best_start == -1 or idx < best_start):
                    best_start = idx + len(key)
            if best_start == -1:
                return ""
            
            best_end = len(content)
            for key in end_keys:
                idx = content.find(key, best_start)
                if idx != -1 and idx < best_end:
                    best_end = idx
            return content[best_start:best_end].strip()

        for chunk in chunks:
            if not chunk.strip():
                continue
            front = extract_value(chunk, start_front_keys, end_front_keys)
            back = extract_value(chunk, start_back_keys, end_back_keys)
            
            if not front:
                front_match = re.search(r'(?:■表（問題）：|■表\(問題\)：|■表：|■表|表（問題）：|表\(問題\)：|表：|■問題)[：:\s]*([\s\S]*?)(?=■裏|裏（解答|■解答|■重要度|$)', chunk)
                if front_match:
                    front = front_match.group(1).strip()
            if not back:
                back_match = re.search(r'(?:■裏（解答・解説）：|■裏\(解答・解説\)：|■裏：|■裏|裏（解答・解説）：|裏\(解答・解説\)：|裏：|■解答)[：:\s]*([\s\S]*?)(?=■重要度|重要度|$)', chunk)
                if back_match:
                    back = back_match.group(1).strip()
                    
            if front or back:
                if not front: front = "（問題未入力）"
                if not back: back = "（解答未入力）"
                
                # 重要度の指定がない場合は自動的にデフォルト値「3」を割り当て
                importance = 3
                imp_str = extract_value(chunk, ['■重要度：', '■重要度:', '重要度：', '重要度:'], ['【カード', '■表', '表（問題）', '■問題'])
                if imp_str:
                    star_count = imp_str.count('★')
                    if 0 < star_count <= 5:
                        importance = star_count
                    else:
                        num_match = re.search(r'[0-5]', imp_str)
                        if num_match:
                            importance = int(num_match.group(0))
                else:
                    star_match = re.search(r'(?:重要度|★)[：:\s]*([0-5])', chunk)
                    if star_match:
                        importance = int(star_match.group(1))
                    else:
                        star_count = chunk.count('★')
                        if 0 < star_count <= 5:
                            importance = star_count
                
                parsed_cards.append({
                    "id": f"card-imported-{int(datetime.now().timestamp())}-{random.randint(1000,9999)}",
                    "deckId": target_deck_id,
                    "front": front,
                    "back": back,
                    "importance": importance,
                    "createdAt": datetime.now().isoformat()
                })
        return parsed_cards

    # 2. CSV / Markdown 形式の標準解析（フォールバック）
    # (省略せずに完全にサポートします)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if len(lines) >= 2 and ("," in lines[0] or "\t" in lines[0]):
        # CSV形式
        cols = [c.lower() for c in lines[0].split(',')]
        f_idx = next((i for i, c in enumerate(cols) if 'front' in c or '問題' in c or 'q' in c), 0)
        b_idx = next((i for i, c in enumerate(cols) if 'back' in c or '解答' in c or 'a' in c), 1)
        imp_idx = next((i for i, c in enumerate(cols) if 'importance' in c or '重要度' in c or '星' in c), -1)

        for l in lines[1:]:
            parts = l.split(',')
            if len(parts) >= 2:
                front = parts[f_idx].replace('"', '').strip()
                back = parts[b_idx].replace('"', '').strip()
                importance = 3 # 重要度指定なしはデフォルト3
                if imp_idx != -1 and len(parts) > imp_idx:
                    try:
                        importance = int(parts[imp_idx].replace('"', '').strip())
                    except:
                        pass
                parsed_cards.append({
                    "id": f"card-imported-{int(datetime.now().timestamp())}-{random.randint(1000,9999)}",
                    "deckId": target_deck_id,
                    "front": front,
                    "back": back,
                    "importance": importance,
                    "createdAt": datetime.now().isoformat()
                })
    else:
        # Markdown形式
        current_front = ""
        current_back = ""
        current_importance = 3 # デフォルト3
        
        for line in lines:
            if line.startswith("### Q:") or line.startswith("Q:"):
                if current_front and current_back:
                    parsed_cards.append({
                        "id": f"card-imported-{int(datetime.now().timestamp())}-{random.randint(1000,9999)}",
                        "deckId": target_deck_id,
                        "front": current_front,
                        "back": current_back,
                        "importance": current_importance,
                        "createdAt": datetime.now().isoformat()
                    })
                    current_front, current_back, current_importance = "", "", 3
                current_front = line.replace("### Q:", "").replace("Q:", "").strip()
            elif line.startswith("- **A**:") or line.startswith("- A:") or line.startswith("**A**"):
                current_back = line.replace("- **A**:", "").replace("- A:", "").replace("**A**:", "").strip()
            elif "重要度" in line or "★" in line:
                star_match = re.search(r'[0-5]', line)
                if star_match:
                    current_importance = int(star_match.group(0))
                    
        if current_front and current_back:
            parsed_cards.append({
                "id": f"card-imported-{int(datetime.now().timestamp())}-{random.randint(1000,9999)}",
                "deckId": target_deck_id,
                "front": current_front,
                "back": current_back,
                "importance": current_importance,
                "createdAt": datetime.now().isoformat()
            })
            
    return parsed_cards


# ------------------------------------------------------------------
# UI & メインメニューナビゲーション
# ------------------------------------------------------------------
st.markdown('<h1 class="main-title">🎴 FlashMaster</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">効率的な暗記学習を支える、あなた専用のインテリジェント・カードシステム</p>', unsafe_allow_html=True)

menu = st.sidebar.radio(
    "メニュー切り替え",
    ["📊 ダッシュボード", "📂 デッキ（問題集）管理", "🎴 カード編集・登録", "📖 暗記＆クイズテスト", "💾 データバックアップ・復元"]
)

# ------------------------------------------------------------------
# 📊 ダッシュボード表示
# ------------------------------------------------------------------
if menu == "📊 ダッシュボード":
    st.header("📊 学習統計ダッシュボード")
    
    # 指標カード
    c1, c2, c3 = st.columns(3)
    c1.metric("総デッキ数", len(st.session_state.decks))
    c2.metric("総暗記カード数", len(st.session_state.cards))
    c3.metric("完了したテストセッション", len(st.session_state.sessions))
    
    # グラフ描画
    st.subheader("📈 日別・テスト正解数の推移")
    if len(st.session_state.sessions) > 0:
        df_sess = pd.DataFrame(st.session_state.sessions)
        df_sess['accuracy'] = (df_sess['score'] / df_sess['totalCards'] * 100).round(1)
        st.line_chart(df_sess.set_index('date')['accuracy'])
    else:
        st.info("まだテスト履歴がありません。テストを完了すると統計が表示されます。")
        
    # 苦手カード
    st.subheader("⚠️ 苦手カード克服リスト")
    if len(st.session_state.weak_cards) > 0:
        for idx, item in enumerate(st.session_state.weak_cards):
            st.warning(f"**{idx+1}. {item['front']}** （間違えた回数: {item['incorrectCount']}回）")
    else:
        st.success("素晴らしい！現在苦手登録されたカードはありません。")

# ------------------------------------------------------------------
# 📂 デッキ管理
# ------------------------------------------------------------------
elif menu == "📂 デッキ（問題集）管理":
    st.header("📂 デッキ（問題集）管理")
    
    # デッキ一覧表示
    st.subheader("現在のデッキ一覧")
    for d in st.session_state.decks:
        with st.container():
            col_d1, col_d2 = st.columns([4, 1])
            with col_d1:
                st.markdown(f"### 📦 {d['name']}")
                st.write(d['description'])
                card_count = len([c for c in st.session_state.cards if c['deckId'] == d['id']])
                st.caption(f"登録カード数: {card_count} 枚 | 作成日: {d['createdAt'][:10]}")
            with col_d2:
                if st.button("デッキ削除", key=f"del-deck-{d['id']}"):
                    st.session_state.decks = [x for x in st.session_state.decks if x['id'] != d['id']]
                    st.session_state.cards = [x for x in st.session_state.cards if x['deckId'] != d['id']]
                    st.rerun()
            st.divider()
            
    # 新規デッキ追加
    st.subheader("➕ 新規デッキを立ち上げる")
    new_d_name = st.text_input("デッキ名", placeholder="例：基本英会話フレーズ")
    new_d_desc = st.text_area("デッキの説明", placeholder="日常会話で使える重要センテンス集")
    if st.button("デッキを追加する"):
        if new_d_name.strip():
            new_id = f"deck-{int(datetime.now().timestamp())}"
            st.session_state.decks.append({
                "id": new_id,
                "name": new_d_name.strip(),
                "description": new_d_desc.strip(),
                "createdAt": datetime.now().isoformat()
            })
            st.success(f"新規デッキ「{new_d_name}」を作成しました！")
            st.rerun()

# ------------------------------------------------------------------
# 🎴 カード編集・登録
# ------------------------------------------------------------------
elif menu == "🎴 カード編集・登録":
    st.header("🎴 カードの管理・追加")
    
    # デッキ選択
    deck_options = {d['id']: d['name'] for d in st.session_state.decks}
    if not deck_options:
        st.warning("まずデッキを作成してください。")
    else:
        selected_deck_id = st.selectbox("管理・編集対象のデッキを選択", list(deck_options.keys()), format_func=lambda x: deck_options[x])
        
        # --- 重要度の一括設定機能 ---
        st.subheader("⭐ 重要度（星評価）の一括変更")
        with st.expander("保存済みのカードを一括更新する"):
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                bulk_stars = st.slider("変更後の重要度 (星評価)", 0, 5, 3)
            with col_b2:
                bulk_scope = st.selectbox("適用する範囲", ["このデッキのみ", "すべてのカード"])
                
            if st.button("一括更新を適用する"):
                for c in st.session_state.cards:
                    if bulk_scope == "すべてのカード" or c['deckId'] == selected_deck_id:
                        c['importance'] = bulk_stars
                st.success("重要度を一括設定しました！")
                st.rerun()
                
        # --- 新規カード登録フォーム ---
        st.subheader("➕ 新しい暗記カードを登録する")
        c_front = st.text_input("表面（問題）を入力")
        c_back = st.text_area("裏面（解答・解説）を入力")
        
        # 評価指定がない場合は自動的に「星0 (評価なし)」
        c_importance = st.slider("重要度 (0なら星なし/評価なし)", 0, 5, 0)
        
        if st.button("カードを登録"):
            if c_front.strip() and c_back.strip():
                new_card_id = f"card-{int(datetime.now().timestamp())}-{random.randint(100,999)}"
                # カードを保存
                st.session_state.cards.append({
                    "id": new_card_id,
                    "deckId": selected_deck_id,
                    "front": c_front.strip(),
                    "back": c_back.strip(),
                    "importance": c_importance,
                    "createdAt": datetime.now().isoformat()
                })
                
                # 入力内容を簡潔にまとめ、後で変更するアドバイスを添える
                st.success("🎉 新しいカードを登録しました！")
                st.info(f"""
                **【入力内容のまとめ】**
                - 表面: {c_front}
                - 裏面: {c_back}
                - 重要度: {'★' * c_importance if c_importance > 0 else '評価なし (星0)'}
                
                💡 *重要度を後で変更したい場合は、上の「一括更新」を使用するか、下のカード編集機能から「星5に変更」のように個別に変更が可能です。*
                """)
                st.rerun()
                
        # 登録済みのカード一覧
        st.subheader("登録されているカード一覧")
        deck_cards = [c for c in st.session_state.cards if c['deckId'] == selected_deck_id]
        
        if not deck_cards:
            st.info("このデッキにはまだカードがありません。上のフォームから登録してください。")
        else:
            for idx, c in enumerate(deck_cards):
                with st.expander(f"NO.{idx+1}: {c['front'][:40]}"):
                    # 個別編集
                    edit_front = st.text_input("表面", c['front'], key=f"f-{c['id']}")
                    edit_back = st.text_area("裏面", c['back'], key=f"b-{c['id']}")
                    edit_stars = st.slider("重要度", 0, 5, c['importance'], key=f"s-{c['id']}")
                    
                    col_act1, col_act2 = st.columns(2)
                    with col_act1:
                        if st.button("変更を保存する", key=f"save-{c['id']}"):
                            c['front'] = edit_front
                            c['back'] = edit_back
                            c['importance'] = edit_stars
                            st.success("カードを更新しました。")
                            st.rerun()
                    with col_act2:
                        if st.button("このカードを削除", key=f"del-{c['id']}"):
                            st.session_state.cards = [x for x in st.session_state.cards if x['id'] != c['id']]
                            st.error("カードを削除しました。")
                            st.rerun()

# ------------------------------------------------------------------
# 📖 暗記＆クイズテスト
# ------------------------------------------------------------------
elif menu == "📖 暗記＆クイズテスト":
    st.header("📖 暗記カード＆選択クイズ")
    
    deck_options = {d['id']: d['name'] for d in st.session_state.decks}
    if not deck_options:
        st.warning("暗記用のデッキがありません。")
    else:
        sel_deck = st.selectbox("学習するデッキを選択", list(deck_options.keys()), format_func=lambda x: deck_options[x])
        mode = st.radio("学習モード", ["🎴 暗記フラッシュカード", "✏️ 4択クイズテスト"])
        
        active_cards = [c for c in st.session_state.cards if c['deckId'] == sel_deck]
        
        if not active_cards:
            st.error("このデッキにはカードが登録されていません。")
        else:
            # --------------------------
            # 1. 暗記フラッシュカードモード
            # --------------------------
            if mode == "🎴 暗記フラッシュカード":
                if st.session_state.study_index >= len(active_cards):
                    st.session_state.study_index = 0
                    
                card = active_cards[st.session_state.study_index]
                
                st.write(f"進捗: {st.session_state.study_index + 1} / {len(active_cards)}")
                
                # 重要度星表示
                stars = '★' * card['importance'] if card['importance'] > 0 else '評価なし (星0)'
                st.caption(f"重要度: {stars}")
                
                # カード面表示
                if not st.session_state.study_flipped:
                    st.markdown(f'<div class="flashcard-box"><div class="flashcard-text">{card["front"]}</div></div>', unsafe_allow_html=True)
                    if st.button("カードをめくる 🔄", use_container_width=True):
                        st.session_state.study_flipped = True
                        st.rerun()
                else:
                    st.markdown(f'<div class="flashcard-box flashcard-back"><div class="flashcard-text">{card["back"]}</div></div>', unsafe_allow_html=True)
                    col_f1, col_f2 = st.columns(2)
                    with col_f1:
                        if st.button("覚えた！ 👍", use_container_width=True):
                            st.session_state.study_index = (st.session_state.study_index + 1) % len(active_cards)
                            st.session_state.study_flipped = False
                            st.rerun()
                    with col_f2:
                        if st.button("忘れた... ❌", use_container_width=True):
                            # 苦手リストへ追加
                            if not any(w['cardId'] == card['id'] for w in st.session_state.weak_cards):
                                st.session_state.weak_cards.append({
                                    "cardId": card["id"],
                                    "front": card["front"],
                                    "incorrectCount": 1
                                })
                            else:
                                for w in st.session_state.weak_cards:
                                    if w['cardId'] == card['id']:
                                        w['incorrectCount'] += 1
                            st.session_state.study_index = (st.session_state.study_index + 1) % len(active_cards)
                            st.session_state.study_flipped = False
                            st.rerun()
            
            # --------------------------
            # 2. 4択クイズテストモード
            # --------------------------
            else:
                st.subheader("✏️ 4択理解度テスト")
                
                # シャッフル準備
                if not st.session_state.test_shuffled_cards:
                    st.session_state.test_shuffled_cards = list(active_cards)
                    random.shuffle(st.session_state.test_shuffled_cards)
                    st.session_state.study_index = 0
                    st.session_state.test_answers = []
                    
                if st.session_state.study_index < len(st.session_state.test_shuffled_cards):
                    current_card = st.session_state.test_shuffled_cards[st.session_state.study_index]
                    st.write(f"問題: {st.session_state.study_index + 1} / {len(st.session_state.test_shuffled_cards)}")
                    st.markdown(f"### Q. 次のカードの意味を4肢から選択してください：\n`{current_card['front']}`")
                    
                    # 選択肢の生成
                    if not st.session_state.test_options:
                        wrong_cards = [c for c in active_cards if c['id'] != current_card['id']]
                        wrong_options = [wc['back'] for wc in random.sample(wrong_cards, min(len(wrong_cards), 3))]
                        options = wrong_options + [current_card['back']]
                        random.shuffle(options)
                        st.session_state.test_options = options
                        
                    choice = st.radio("選択肢を選んで回答を送信してください：", st.session_state.test_options, key=f"q-{st.session_state.study_index}")
                    
                    if st.button("回答する"):
                        is_correct = (choice == current_card['back'])
                        st.session_state.test_answers.append(is_correct)
                        
                        if is_correct:
                            st.success("⭕ 正解です！")
                        else:
                            st.error(f"❌ 不正解です。 正解：{current_card['back']}")
                            
                        # 次の問題へ進むための準備
                        st.session_state.study_index += 1
                        st.session_state.test_options = []
                        st.button("次の問題に進む ➡️")
                else:
                    # テスト結果発表
                    correct_count = sum(st.session_state.test_answers)
                    total_count = len(st.session_state.test_shuffled_cards)
                    score_pct = int((correct_count / total_count) * 100) if total_count > 0 else 0
                    
                    st.balloons()
                    st.success(f"🎉 テスト完了！お疲れ様でした！")
                    st.metric("正解率", f"{score_pct}%", f"{correct_count} / {total_count}問正解")
                    
                    # 履歴を保存
                    if st.button("テストセッション履歴をセーブして終了"):
                        st.session_state.sessions.append({
                            "id": f"sess-{int(datetime.now().timestamp())}",
                            "deckId": sel_deck,
                            "deckName": deck_options[sel_deck],
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "totalCards": total_count,
                            "score": correct_count
                        })
                        # ステートリセット
                        st.session_state.test_shuffled_cards = []
                        st.session_state.test_answers = []
                        st.session_state.study_index = 0
                        st.rerun()

# ------------------------------------------------------------------
# 💾 データバックアップ・復元
# ------------------------------------------------------------------
elif menu == "💾 データバックアップ・復元":
    st.header("💾 バックアップ & データインポート")
    
    tab_ex, tab_im = st.tabs(["📤 エクスポート（保存）", "📥 インポート（読み込み）"])
    
    with tab_ex:
        st.subheader("カードデータのエクスポート")
        format_choice = st.radio("保存フォーマット", ["CSV形式", "Markdown形式"])
        
        # デッキ選択
        deck_opts = {"all": "すべてのデッキ"}
        deck_opts.update({d['id']: d['name'] for d in st.session_state.decks})
        sel_export_deck = st.selectbox("エクスポート対象", list(deck_opts.keys()), format_func=lambda x: deck_opts[x])
        
        # ターゲットカードの抽出
        if sel_export_deck == "all":
            target_cards = st.session_state.cards
        else:
            target_cards = [c for c in st.session_state.cards if c['deckId'] == sel_export_deck]
            
        if format_choice == "CSV形式":
            output_lines = ["DeckName,Front,Back,Importance"]
            for c in target_cards:
                d_name = next((d['name'] for d in st.session_state.decks if d['id'] == c['deckId']), '未分類')
                output_lines.append(f'"{d_name}","{c["front"]}","{c["back"]}",{c["importance"]}')
            export_text = "\n".join(output_lines)
        else:
            # Markdown
            md_blocks = []
            for d in st.session_state.decks:
                if sel_export_deck != "all" and d['id'] != sel_export_deck:
                    continue
                d_cards = [c for c in st.session_state.cards if c['deckId'] == d['id']]
                card_blocks = [f"### Q: {c['front']}\n- **A**: {c['back']}\n- **重要度**: ★ {c['importance']}\n" for c in d_cards]
                md_blocks.append(f"# デッキ: {d['name']}\n\n" + "\n".join(card_blocks))
            export_text = "\n\n---\n\n".join(md_blocks)
            
        st.text_area("生成されたバックアップテキスト", export_text, height=200)
        st.download_button(
            "ファイルとして保存",
            export_text,
            file_name=f"flashcard_backup.{'csv' if format_choice == 'CSV形式' else 'md'}"
        )
        
    with tab_im:
        st.subheader("データのインポート（自動解析）")
        st.markdown("""
        **【インポート形式の自動解析について】**
        FlashMasterは、貼り付けられたデータの形式にこだわらず、自動的に情報を読み取ることができます。
        
        - **標準CSV・TSV形式** (ヘッダー行つき)
        - **Markdown形式** (### Q:、- **A**:、重要度: ★ 等)
        - **カスタム暗記テキスト形式**
          - 「【カードNO. X】■表（問題）：... ■裏（解答・解説）：...」のような形式でも、自動的に問題と解答を完璧にマッピングして登録します。
          - 「重要度」の指定がない場合は、自動的にデフォルト値として **「3」** を割り当てます。
        """)
        
        target_import_deck = st.selectbox("インポート先デッキ", list({d['id']: d['name'] for d in st.session_state.decks}.items()), format_func=lambda x: x[1])
        
        import_text = st.text_area("インポートデータテキストを貼り付けてください：", height=250)
        
        if st.button("解析を開始してデータをインポート"):
            if import_text.strip():
                try:
                    parsed = parse_imported_text(import_text, target_import_deck[0])
                    if len(parsed) > 0:
                        st.session_state.cards.extend(parsed)
                        st.success(f"正常に解析を完了しました！ {len(parsed)}枚の新規カードを 「{target_import_deck[1]}」 に登録しました。")
                        st.rerun()
                    else:
                        st.error("入力テキストから有効な問題・解答を抽出できませんでした。フォーマットを確認してください。")
                except Exception as e:
                    st.error(f"インポート解析中にエラーが発生しました: {str(e)}")
            else:
                st.warning("テキストを入力してください。")
