import streamlit as st
import pandas as pd
import random
import os

# --- 設定 ---
st.set_page_config(page_title="英検2級 合格特訓 Web", layout="centered")

# --- データ読み込み関数 ---
def load_data(filename):
    file_path = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = [line.strip().split(",") for line in f if "," in line]
            return [(d[0].strip(), d[1].strip()) for d in data]
    return []

# --- セッション状態の初期化（Webで変数を保持するために必要） ---
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = []
    st.session_state.current_idx = 0
    st.session_state.score = 0
    st.session_state.options = []
    st.session_state.is_answered = False
    st.session_state.quiz_active = False

# --- メイン画面 ---
st.title("📚 英検2級 合格特訓 Web")

# サイドメニュー
mode = st.sidebar.radio("学習項目を選択", ["英単語", "英熟語"])
num_q = st.sidebar.slider("出題数", 5, 20, 10)

# クイズ開始ボタン
if not st.session_state.quiz_active:
    if st.button(f"{mode}クイズを開始する", use_container_width=True):
        filename = "wordlist.txt" if mode == "英単語" else "idiomlist.txt"
        all_data = load_data(filename)
        if all_data:
            st.session_state.quiz_data = random.sample(all_data, min(len(all_data), num_q))
            st.session_state.current_idx = 0
            st.session_state.score = 0
            st.session_state.quiz_active = True
            st.session_state.is_answered = False
            st.rerun()
        else:
            st.error(f"{filename} が見つかりません。")

# クイズ本編
if st.session_state.quiz_active:
    q_list = st.session_state.quiz_data
    idx = st.session_state.current_idx
    
    if idx < len(q_list):
        word, correct_meaning = q_list[idx]
        
        # 選択肢の作成（最初の1回だけ実行）
        if not st.session_state.is_answered and not st.session_state.options:
            all_meanings = [m for w, m in q_list if m != correct_meaning]
            options = random.sample(all_meanings, min(len(all_meanings), 3)) + [correct_meaning]
            random.shuffle(options)
            st.session_state.options = options

        st.subheader(f"第 {idx + 1} 問 / {len(q_list)}")
        st.info(f"### {word}")

        # 4択ボタン
        for opt in st.session_state.options:
            if st.button(opt, use_container_width=True, disabled=st.session_state.is_answered):
                st.session_state.is_answered = True
                if opt == correct_meaning:
                    st.session_state.score += 1
                    st.success("⭕ 正解！")
                else:
                    st.error(f"❌ 残念！ 正解は: {correct_meaning}")
                st.button("次の問題へ", on_click=lambda: (
                    setattr(st.session_state, 'current_idx', st.session_state.current_idx + 1),
                    setattr(st.session_state, 'is_answered', False),
                    setattr(st.session_state, 'options', [])
                ))
    else:
        # 結果発表
        st.balloons()
        st.header("🎉 クイズ終了！")
        st.metric("スコア", f"{st.session_state.score} / {len(q_list)}")
        if st.button("トップに戻る"):
            st.session_state.quiz_active = False
            st.rerun()