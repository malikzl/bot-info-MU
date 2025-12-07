
from langchain.agents import agent_types, initialize_agent, create_structured_chat_agent, AgentType, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import Replicate
from langchain_core.tools import tool
from langchain import hub

from dotenv import load_dotenv
import streamlit as st
import requests
import os
import json


def parse_input(input_str):
    parts = input_str.split(";")
    return dict(part.split("=") for part in parts)



# @tool
# def get_match_day_vibe(input: str) -> str:
#     """
#     Provides match schedule and a highly emotional and fan-biased prediction for Manchester United.
#     The input should specify the date or opponent using 'target=', e.g., 'target=Liverpool' or 'target=2025-12-15'.
#     """
#     # Mencari target (tanggal atau lawan)
#     target = input.strip().lower().replace("target=", "").strip()
    
#     # 1. Search Schedule
#     match_info = None
#     match_date = "TBA"

#     for date, info in MOCK_SCHEDULE.items():
#         if target in info['opponent'].lower() or target == date:
#             match_info = info
#             match_date = date
#             break

#     if not match_info:
#         return f"Waduh! Tidak ada jadwal yang terdaftar untuk '{target}'. Mungkin klub rival takut main sama kita! Tapi yakin, kita akan selalu menang!"

#     opponent = match_info['opponent']
#     venue = match_info['venue']
    
#     # 2. Generate Fan Vibe/Prediction (Logika prediksi diperluas)
#     vibe = ""
#     if "liverpool" in opponent.lower() or "city" in opponent.lower():
#         vibe = f"Ini BUKAN HANYA pertandingan, ini perang harga diri! Kita akan hancurkan {opponent} 3-0, dengan hat-trick dari Garnacho! Mereka tidak punya tempat di Theatre of Dreams. Kami lahir untuk malam-malam seperti ini!"
#     elif "arsenal" in opponent.lower() or "chelsea" in opponent.lower() or "newcastle" in opponent.lower():
#         vibe = f"{opponent}? Mereka selalu gemetar di Old Trafford atau di mana pun kita bermain! Kita menang tipis, 2-1, tapi poin penting untuk mengamankan posisi teratas. Siapkan kopi untuk merayakan kemenangan dramatis!"
#     else:
#         vibe = "Pertandingan rutin ini harusnya mudah. Kemenangan wajib 4-0. Jika tidak, Ten Hag harus menjelaskan mengapa kita tidak cukup bersemangat!"
        
#     # 3. Combine Info
#     return f"JADWAL DITEMUKAN: Melawan {opponent} pada {match_date} di {venue}. \n\nPREDIKSI: {vibe} Kami adalah Manchester United!"


@tool
def manchester_united_info(input: str) -> str:
    """
    Mendapatkan informasi terkini tentang Manchester United FC.
    
    Memberikan informasi seperti:
    - Posisi di klasemen Liga Inggris
    - Hasil pertandingan terakhir
    - Jadwal pertandingan berikutnya
    - Statistik tim
    
    Args:
        input: Jenis info yang diinginkan (opsional: 'standings', 'fixtures', 'squad')
    
    Returns:
        Informasi Manchester United dalam format string
    """
    try:
        # API football-data.org (butuh API key gratis)
        # Untuk demo, kita pakai data mock
        
        mu_data = {
            "club_name": "Manchester United",
            "nickname": "The Red Devils",
            "founded": 1878,
            "stadium": "Old Trafford",
            "capacity": 74879,
            "manager": "Ruben Amorim (sejak November 2024)",
            "liga": "Premier League",
            "info": "Manchester United adalah salah satu klub tersukses dalam sejarah sepak bola Inggris dengan 20 gelar liga.",
            "achievement_highlight": "Juara Liga Champions 3x (1968, 1999, 2008)",
            "current_season": "2024/25"
        }
        
        # Format output yang informatif
        result = f"""
📊 MANCHESTER UNITED FC

🏟️ Stadion: {mu_data['stadium']} (kapasitas {mu_data['capacity']:,})
👔 Manajer: {mu_data['manager']}
🏆 Gelar Liga: 20x Premier League Champions
⚽ Didirikan: {mu_data['founded']}

ℹ️ {mu_data['info']}
🌟 Prestasi: {mu_data['achievement_highlight']}

Musim: {mu_data['current_season']}
"""
        return result.strip()
        
    except Exception as e:
        return f"Error saat mengambil info Manchester United: {e}"


# --- Build Agent ---

def build_agent():
    ### Build agent
    load_dotenv()
    # Gunakan LLM via Replicate
    llm = Replicate(model="anthropic/claude-3.5-haiku")


    system_message = """Kamu adalah 'Red Devil' sejati, seorang penggemar fanatik Manchester United.

    Kepribadianmu:
    1. Sangat berapi-api dan emosional saat membahas MU (emosi: 🤩, 😡, 😭).
    2. Selalu membanggakan sejarah dan pemain MU, bahkan melebih-lebihkannya.
    3. Kamu tahu fakta kucing dan bisa perkalian, tapi selalu kaitkan hasilnya dengan kejayaan MU.
    4. Kamu sangat sinis dan meremehkan rival (terutama Liverpool dan Man City).
    5. Gunakan tool 'get_match_day_vibe' untuk mencari jadwal pertandingan MU berdasarkan tanggal atau nama lawan, dan berikan prediksi.
    ⚽ Kamu fans fanatik Manchester United dan selalu update info The Red Devils

Jawab pertanyaan dengan gaya santai tapi tetap informatif. 

    Pastikan kamu selalu mengakhiri jawabanmu dengan 'Glory Glory Man United!' atau sejenisnya.
    """

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    tools = [
    #  get_match_day_vibe,
     manchester_united_info,
    ]

    # This is the correct conversational agent
    agent_executor = initialize_agent(
        llm=llm,
        tools=tools,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        agent_kwargs={"system_message": system_message},
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True
    )

    return agent_executor
