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
    st.session_state.wrong_list = []  # 苦手リスト：辞書のリスト [{'kanji':..., 'read':..., 'correct_count': 0}]
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'answered' not in st.session_state:
    st.session_state.answered = False
if 'test_data' not in st.session_state:
    st.session_state.test_data = []

# --- クイズエンジン（共通関数） ---
def quiz_engine(data_list):
    if not data_list:
        st.info("問題がありません。")
        return

    # すべての問題が終わったかチェック
    if st.session_state.current_question >= len(data_list):
        st.balloons()
        st.success(st.session_state.wrong_list)
        st.write(f"🎉 テスト終了！ あなたのスコアは {st.session_state.score} / {len(data_list)} です！")
        
        # 苦手リストの現在の状態を表示
        st.write("---")
        st.write("📋 現在の苦手漢字リスト（3回正解でクリア）：")
        if st.session_state.wrong_list:
            for w in st.session_state.wrong_list:
                st.write(f"・{w['kanji']}（{w['read']}） - あと {3 - w.get('correct_count', 0)} 回正解で克服！")
        else:
            st.success("完璧！苦手な漢字はありません。")
            
        if st.button("もう一度挑戦する", key="retry_btn"):
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.rerun()
        return

    # 現在の問題を取得
    current_q = data_list[st.session_state.current_question]
    idx = st.session_state.current_question

    st.subheader(f"第 {idx + 1} 問")
    st.info(f"「 {current_q['kanji']} 」 の読み方は？")

    # ユーザーの入力
    user_input = st.text_input("ひらがなで入力してください：", key=f"input_{idx}").strip()

    col1, col2 = st.columns(2)

    with col1:
        # 回答するボタン
        if st.button("回答する", key=f"ans_{idx}"):
            st.session_state.answered = True
            if user_input == current_q['read']:
                st.session_state.score += 1
                st.session_state.is_correct = True
                
                # 復習モード中の場合、正解数をカウントアップ
                if st.session_state.mode == "review":
                    for w in st.session_state.wrong_list:
                        if w['kanji'] == current_q['kanji']:
                            w['correct_count'] = w.get('correct_count', 0) + 1
                            break
            else:
                st.session_state.is_correct = False
                # 間違えた場合：通常テストでも復習モードでも、苦手リストに未登録なら追加
                # 正解カウント(correct_count)を0で初期化して登録
                if not any(w['kanji'] == current_q['kanji'] for w in st.session_state.wrong_list):
                    st.session_state.wrong_list.append({
                        'kanji': current_q['kanji'],
                        'read': current_q['read'],
                        'correct_count': 0
                    })
                else:
                    # すでにリストにあって、間違えた場合は正解カウンターをリセット（厳しくする場合）
                    for w in st.session_state.wrong_list:
                        if w['kanji'] == current_q['kanji']:
                            w['correct_count'] = 0

    with col2:
        # わからないボタン
        if st.button("わからない", key=f"skip_{idx}"):
            st.session_state.answered = True
            st.session_state.is_correct = False
            # 苦手リストに未登録なら追加
            if not any(w['kanji'] == current_q['kanji'] for w in st.session_state.wrong_list):
                st.session_state.wrong_list.append({
                    'kanji': current_q['kanji'],
                    'read': current_q['read'],
                    'correct_count': 0
                })
            else:
                # わからないを押した場合もカウンターをリセット
                for w in st.session_state.wrong_list:
                    if w['kanji'] == current_q['kanji']:
                        w['correct_count'] = 0

    # 回答後のフィードバック表示
    if st.session_state.answered:
        if st.session_state.is_correct:
            st.success("⭕ 正解です！")
        else:
            st.error(f"❌ 残念！ 正解は「 {current_q['read']} 」でした。")

        # 「次へ進む」ボタンを押したときに、3回正解した漢字を削除する判定を行う
        if st.button("次へ進む", key=f"next_{idx}"):
            # 3回正解した漢字を苦手リストから削除
            st.session_state.wrong_list = [w for w in st.session_state.wrong_list if w.get('correct_count', 0) < 3]
            
            st.session_state.current_question += 1
            st.session_state.answered = False
            st.rerun()

# --- 2. サイドバーメニュー ---
with st.sidebar:
    st.title("🍀 メニュー")
    menu = st.radio("メニューを選んでね", ["🏠 ホーム", "✍️ テスト開始", "🔥 復習モード"])
    
    st.write("---")
    st.write(f"現在の苦手漢字: {len(st.session_state.wrong_list)} 個")

# --- 3. 画面の切り替え処理 ---
if menu == "🏠 ホーム":
    st.title("🏠 漢字クイズアプリへようこそ！")
    st.write("サイドバーからメニューを選んでね。")
    st.write("・「テスト開始」では全体からランダムに10問出題されます。")
    st.write("・「復習モード」では、これまでに間違えた苦手な漢字だけが出題されます。")
    st.write("💡 **新機能**：苦手リストに入った漢字は、復習モードで**3回正解**するとリストから消えます！")

elif menu == "✍️ テスト開始":
    st.title("✍️ 実力テスト (10問)")
    
    # テスト開始時の初期化
    if 'mode' not in st.session_state or st.session_state.mode != "test":
        st.session_state.current_question = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.session_state.mode = "test"
        
        # 全データから10問をランダムに選んで固定
        sample_size = min(10, len(st.session_state.all_kanji_data))
        st.session_state.test_data = random.sample(st.session_state.all_kanji_data, sample_size)
    
    quiz_engine(st.session_state.test_data)

elif menu == "🔥 復習モード":
    st.title("🔥 苦手克服テスト")
    
    # 苦手リストが空っぽの場合の処理
    if not st.session_state.wrong_list:
        st.success("🎉 現在、苦手な漢字はありません！完璧です！")
    else:
        # 復習モード開始時の初期化
        if 'mode' not in st.session_state or st.session_state.mode != "review":
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.session_state.mode = "review"
            
            # 苦手リストに入っている漢字をシャッフルして今回のテストデータにする
            # リストのコピーを作ってシャッフル
            review_data = list(st.session_state.wrong_list)
            random.shuffle(review_data)
            st.session_state.test_data = review_data
            
        st.write(f"現在の苦手漢字 {len(st.session_state.test_data)} 問に挑戦中！")
        quiz_engine(st.session_state.test_data)
