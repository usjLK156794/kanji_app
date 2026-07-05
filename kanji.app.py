import streamlit as st
import random
# data.py から KANJI_LIST を読み込む
try:
    from data import KANJI_LIST
except ImportError:
    st.error("data.py が見つかりません。同じフォルダに作成してください。")
    st.stop()

# --- 1. テストデータの初期化 ---
if 'all_kanji_data' not in st.session_state:
    st.session_state.all_kanji_data = KANJI_LIST

# 各種状態の初期化
if 'wrong_list' not in st.session_state:
    st.session_state.wrong_list = []
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'answered' not in st.session_state:
    st.session_state.answered = False

# --- 2. サイドバーメニュー ---
with st.sidebar:
    st.title("🍀 メニュー")
    menu = st.radio("メニューを選んでね", ["🏠 ホーム", "✍️ テスト開始", "🔥 復習モード"])
    
    st.write("---")
    st.write(f"現在の苦手漢字: {len(st.session_state.wrong_list)} 個")
    if st.button("全データをリセット"):
        st.session_state.clear()
        st.rerun()

# --- 3. 関数 ---
def get_choices(correct_answer):
    # すべての読み候補を取得
    all_reads = [item['read'] for item in st.session_state.all_kanji_data]
    other_reads = [r for r in all_reads if r != correct_answer]
    # ダミーを最大3つ選ぶ
    num_wrong = min(len(other_reads), 3)
    wrong_choices = random.sample(other_reads, num_wrong)
    choices = wrong_choices + [correct_answer]
    random.shuffle(choices)
    return choices

def quiz_engine(data_list):
    """クイズを表示する共通エンジン"""
    if not data_list:
        st.info("対象となる漢字がありません。")
        return

    q_idx = st.session_state.current_question
    if q_idx >= len(data_list):
        st.balloons()
        st.header("✨ 終了！")
        st.success(f"スコア: {st.session_state.score} / {len(data_list)}")
        if st.button("結果を確定して戻る"):
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.rerun()
        return

    q_item = data_list[q_idx]
    st.subheader(f"第 {q_idx + 1} 問 / {len(data_list)}")
    st.markdown(f"## 「<span style='color:red'>{q_item['kanji']}</span>」", unsafe_allow_html=True)

    choice_key = f"choices_{q_item['kanji']}"
    if choice_key not in st.session_state:
        st.session_state[choice_key] = get_choices(q_item['read'])
    
    choices = st.session_state[choice_key]

    if not st.session_state.answered:
        for choice in choices:
            if st.button(choice, key=f"btn_{q_idx}_{choice}", use_container_width=True):
                st.session_state.answered = True
                st.session_state.last_choice = choice
                st.rerun()
    else:
        if st.session_state.last_choice == q_item['read']:
            st.success(f"⭕ 正解！")
            if 'last_q_rec' not in st.session_state or st.session_state.last_q_rec != q_idx:
                st.session_state.score += 1
                st.session_state.last_q_rec = q_idx
        else:
            st.error(f"❌ 残念... 正解は「{q_item['read']}」")
            if q_item not in st.session_state.wrong_list:
                st.session_state.wrong_list.append(q_item)
            st.session_state.last_q_rec = q_idx

        if st.button("次の問題へ 👉", type="primary", use_container_width=True):
            st.session_state.current_question += 1
            st.session_state.answered = False
            if 'last_q_rec' in st.session_state: del st.session_state.last_q_rec
            st.rerun()

# --- 4. 画面切り替え ---
if menu == "🏠 ホーム":
    st.title("🏠 漢字テスト対策アプリ")
    st.write("左のメニューからモードを選んでください。")
    if st.session_state.wrong_list:
        st.subheader("📝 復習が必要な漢字：")
        for w in st.session_state.wrong_list:
            st.write(f"・{w['kanji']}（{w['read']}）")
    else:
        st.success("完璧！苦手な漢字はありません。")

elif menu == "✍️ テスト開始":
    st.title("✍️ 実力テスト")
    if 'mode' not in st.session_state or st.session_state.mode != "test":
        st.session_state.current_question = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.session_state.mode = "test"
        random.shuffle(st.session_state.all_kanji_data)
    quiz_engine(st.session_state.all_kanji_data)

elif menu == "🔥 復習モード":
    st.title("🔥 苦手克服")
    if 'mode' not in st.session_state or st.session_state.mode != "review":
        st.session_state.current_question = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.session_state.mode = "review"
        random.shuffle(st.session_state.wrong_list)
    quiz_engine(st.session_state.wrong_list)