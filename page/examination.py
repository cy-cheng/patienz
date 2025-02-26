import streamlit as st 
from model.examiner import create_text_examiner_model
from model.examiner import create_value_examiner_model
import util.dialog as dialog
import util.tools as util
import util.constants as const
import csv
import pandas as pd
import json

ss = st.session_state

util.init(2)
util.note()

def process_examination_result(full_items, result_json):
    examination_result = json.loads(result_json)

    print(examination_result)

    full_items = {item[0]: {
        "chinese_name": item[1],
        "reference_value": item[2],
        "unit": item[3],
    } for item in full_items}

    rows = []

    for data in examination_result['value_type_item']:
        try:
            rows.append({
                "檢驗項目": data['englishName'],
                "中文名稱": full_items[data['englishName']]['chinese_name'],
                "參考值": full_items[data['englishName']]['reference_value'],
                "檢測值": data['value'],
                "單位": full_items[data['englishName']]['unit'],
            })
        except Exception as e:
            print(f"Error: {e}")

    df = pd.DataFrame(rows)
    left_align = lambda x: f"<div style='text-align: left;'>{x}</div>"
    cent_align = lambda x: f"<div style='text-align: center;'>{x}</div>"

    if df.empty:
        return "發生錯誤，請重新檢查。"

    html_table = df.to_html(
        index=False,
        escape=False,
        classes="dataframe table",
        table_id="examination-results",
        col_space="5em",
        formatters=[left_align, left_align, cent_align, cent_align, cent_align],
        justify="center",
    )

    return html_table

column = st.columns([1, 10, 1, 4])

with column[1]:
    selection_container = st.container()
    button_container = st.container() 
    result_container = st.container()

    with selection_container:
        st.header("檢查選擇")

        with open("examination_file/examination_choice.json", "r", encoding="utf-8") as f:
            examination_choice = json.load(f)

        category = st.radio("檢查領域", examination_choice.keys(), horizontal=True)

        if category != None:

            examination = st.radio("檢查項目", examination_choice[category].keys(), horizontal=True)

            if examination != None:
                l, r = int(examination_choice[category][examination]['l']-1), int(examination_choice[category][examination]['r']-1)

                with open("examination_file/examination.csv", "r", encoding="utf-8") as f:
                    sheet = list(csv.reader(f))
                    display_options = [f"{row[1]} {row[0]}" for row in sheet][l:r]
                    full_options = {f"{row[1]} {row[0]}": row for row in sheet}
                    
                # st.write(full_options)
                # st.write(display_options)
                
                if examination in const.default_all:
                    item_names = st.multiselect("檢查細項", options=display_options, default=display_options)
                else:
                    item_names = st.multiselect("檢查細項", display_options)
        
    def render_result():
        with result_container:
            if ss.examination_result != []: st.header("檢查結果")
        
            with st.container(border=True):
                for name, res in ss.examination_result:
                    st.subheader(name)
                    st.markdown(res, unsafe_allow_html=True)

    with button_container: 
        st.container(height=50, border=False)
        if st.button("開始檢查", use_container_width=True) and util.check_progress():
            full_items = [full_options[item] for item in item_names] 

            print(full_items)

            if category != "實驗室檢查" and examination != "快篩":
                create_text_examiner_model(ss.problem, ", ".join([item[0] for item in full_items]))
                with st.spinner("進行檢查中..."):
                    ss.examination_result.append(("、".join([item[1] for item in full_items]), ss.examiner.send_message(f"Please list out the anomalies base on only the examination of the following test: {full_items}").text))

            else:

                create_value_examiner_model(ss.problem, ", ".join([item[0] for item in full_items]))
                with st.spinner("進行檢查中..."):
                    ss.examination_result.append((examination, process_examination_result(full_items, ss.examiner.send_message(f"{full_items}").text)))

            st.rerun()

        if st.button("完成檢查", use_container_width=True) and util.check_progress():
            util.next_page()

    render_result()

with column[3]:
    util.show_patient_profile()

    st.subheader("其他資訊")
    with st.container(border=True):
        util.show_time()

