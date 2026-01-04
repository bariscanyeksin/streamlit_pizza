import requests
from bs4 import BeautifulSoup
import hashlib
import base64
import json
from datetime import datetime
import streamlit as st
import pandas as pd
from typing import Dict, Optional, Any
import matplotlib.pyplot as plt
import io
from pizza_chart import create_pizza_chart
from matplotlib import font_manager as fm
import os

CONFIG = {
    'API_BASE_URL': 'https://www.fotmob.com/api',
    'DEFAULT_LANGUAGE': 'tr,en',
    'MAX_HITS': 50,
    'HEADERS': {
        'accept': '*/*',
        'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }
}

TRANSLATIONS = {
    'en': {
        'player_search': "Player Search",
        'player_search_placeholder': "Example: Yamal",
        'player_search_help': "Enter the player's name here.",
        'player_empty_warning': "Player name is empty. Please enter a search term.",
        'player_not_found': "No player found matching your search.",
        'player_selection': "Player Selection",
        'player_selection_help': "Select the player you want from the list.",
        'pizza_template': "Pizza Template",
        'pizza_template_help': "Although the pizza template is automatically determined according to the selected player's position, you can choose any pizza template you want.",
        'loading_message': "Loading player data...",
        'stats_not_found': "Player stats could not be retrieved.",
        'general_info_error': "Player general information could not be retrieved.",
        'data_load_error': "Error occurred while loading data: {}",
        'download_button': "Download Chart",
        'info_text': """This pizza chart is used to visualize a player's performance in specific statistics. 
        Each slice represents the player's percentile rank among players in the same position in the league/tournament based on a statistic. 
        The size of the slice indicates the player's performance level in that statistic; 
        larger slices represent higher rankings.""",
        'no_player_data': "Player data not found.",
        'templates': {
            'Goalkeeper': "Goalkeeper",
            'Center Back': "Center Back",
            'Right Back - Left Back': "Right Back - Left Back",
            'Central Midfielder': "Central Midfielder",
            'Winger - Attacking Midfielder': "Winger - Attacking Midfielder",
            'Striker': "Striker"
        },
        'season_league_select': "Player | Season - League",
        'season_league_help': "Select the season and league to compare.",
    },
    'tr': {
        'player_search': "Oyuncu Arama",
        'player_search_placeholder': "Örneğin: Yamal",
        'player_search_help': "Oyuncunun ismini buraya girin.",
        'player_empty_warning': "Oyuncu ismi boş. Lütfen arama terimi girin.",
        'player_not_found': "Aramanızla eşleşen oyuncu bulunamadı.",
        'player_selection': "Oyuncu Seçimi",
        'player_selection_help': "Listeden istediğiniz oyuncuyu seçin.",
        'pizza_template': "Pizza Şablonu",
        'pizza_template_help': "Seçilen oyuncunun pozisyonuna göre pizza şablonu otomatik olarak belirlense de istediğiniz pizza şablonunu seçebilirsiniz.",
        'loading_message': "Oyuncu verileri yükleniyor...",
        'stats_not_found': "Oyuncu istatistikleri alınamadı.",
        'general_info_error': "Oyuncu genel bilgileri alınamadı.",
        'data_load_error': "Veri yüklenirken hata oluştu: {}",
        'download_button': "Grafiği İndir",
        'info_text': """Bu pizza grafiği, bir oyuncunun belirli istatistiklerdeki performansını
        görselleştirmek için kullanılır. Her dilim, oyuncunun bir istatistikteki yüzdelik dilime göre ligde/turnuvada aynı pozisyonda oynayan
        oyuncular arasındaki sıralamasını temsil eder. Dilimin büyüklüğü, oyuncunun o istatistikteki performans seviyesini gösterir;
        daha büyük dilimler, daha yüksek sıralamayı ifade eder.""",
        'no_player_data': "Oyuncunun verisi bulunamadı.",
        'templates': {
            'Goalkeeper': "Kaleci",
            'Center Back': "Stoper",
            'Right Back - Left Back': "Sağ Bek - Sol Bek",
            'Central Midfielder': "Merkez Orta Saha",
            'Winger - Attacking Midfielder': "Kanat - Ofansif Orta Saha",
            'Striker': "Santrafor"
        },
        'season_league_select': "Oyuncu | Sezon - Lig",
        'season_league_help': "Karşılaştırılmak istenilen sezonu ve ligi seçin.",
    },
    'fr': {
        'player_search': "Recherche de Joueur",
        'player_search_placeholder': "Exemple : Yamal",
        'player_search_help': "Entrez le nom du joueur ici.",
        'player_empty_warning': "Le nom du joueur est vide. Veuillez saisir un terme de recherche.",
        'player_not_found': "Aucun joueur correspondant à votre recherche n'a été trouvé.",
        'player_selection': "Sélection du Joueur",
        'player_selection_help': "Sélectionnez le joueur souhaité dans la liste.",
        'pizza_template': "Modèle de Pizza",
        'pizza_template_help': "Bien que le modèle de pizza soit automatiquement déterminé en fonction du poste sélectionné du joueur, vous pouvez choisir n'importe quel modèle de pizza.",
        'loading_message': "Chargement des données du joueur...",
        'stats_not_found': "Les statistiques du joueur n'ont pas pu être récupérées.",
        'general_info_error': "Les informations générales du joueur n'ont pas pu être récupérées.",
        'data_load_error': "Une erreur est survenue lors du chargement des données : {}",
        'download_button': "Télécharger le Graphique",
        'info_text': """Ce graphique en pizza est utilisé pour visualiser la performance d'un joueur sur des statistiques spécifiques. 
        Chaque part représente le rang percentile du joueur parmi les joueurs du même poste dans la ligue/le tournoi pour une statistique donnée. 
        La taille de la part indique le niveau de performance du joueur sur cette statistique ; 
        des parts plus grandes représentent des classements plus élevés.""",
        'no_player_data': "Aucune donnée joueur trouvée.",
        'templates': {
            'Goalkeeper': "Gardien de but",
            'Center Back': "Défenseur central",
            'Right Back - Left Back': "Arrière droit - Arrière gauche",
            'Central Midfielder': "Milieu central",
            'Winger - Attacking Midfielder': "Ailier - Milieu offensif",
            'Striker': "Attaquant"
        },
        'season_league_select': "Joueur | Saison - Ligue",
        'season_league_help': "Sélectionnez la saison et la ligue à comparer.",
    }
}

st.set_page_config(
    page_title="Percentile Pizza Chart",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        /* Sidebar içindeki tüm text input elementlerini hedef alma */
        input[id^="text_input"] {
            background-color: #242C3A !important;  /* Arka plan rengi */
        }
    </style>
    """,
    unsafe_allow_html=True
)

plt.rcParams['figure.dpi'] = 300
current_dir = os.path.dirname(os.path.abspath(__file__))

font_path = os.path.join(current_dir, 'fonts', 'Poppins-Regular.ttf')
prop = fm.FontProperties(fname=font_path)

bold_font_path = os.path.join(current_dir, 'fonts', 'Poppins-SemiBold.ttf')
bold_prop = fm.FontProperties(fname=bold_font_path)

def get_version_number():
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'referer': 'https://www.google.com/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }
    
    response = requests.get("https://www.fotmob.com/", headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    version_element = soup.find('span', class_=lambda cls: cls and 'VersionNumber' in cls)
    if version_element:
        return version_element.text.strip()
    else:
        return None
    
version_number = get_version_number()

def get_xmas_pass():
    url = 'https://raw.githubusercontent.com/bariscanyeksin/streamlit_radar/refs/heads/main/xmas_pass.txt'
    response = requests.get(url)
    if response.status_code == 200:
        file_content = response.text
        return file_content
    else:
        print(f"Failed to fetch the file: {response.status_code}")
        return None
    
xmas_pass = get_xmas_pass()

def create_xmas_header(url, password):
    try:
        timestamp = int(datetime.now().timestamp() * 1000)
        request_data = {
            "url": url,
            "code": timestamp,
            "foo": version_number
        }
        
        if not password:
            raise ValueError("Password is missing")
            
        json_string = f"{json.dumps(request_data, separators=(',', ':'))}{password.strip()}"
        signature = hashlib.md5(json_string.encode('utf-8')).hexdigest().upper()
        body = {
            "body": request_data,
            "signature": signature
        }
        return base64.b64encode(json.dumps(body, separators=(',', ':')).encode('utf-8')).decode('utf-8')
    except Exception as e:
        st.error(f"Error generating signature: {str(e)}")
        return None

def headers(player_id):
    api_url = "/api/playerData?id=" + str(player_id)
    xmas_value = create_xmas_header(api_url, xmas_pass)
    
    headers = {
        'accept': '*/*',
        'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': f'https://www.fotmob.com/en-GB/players/{player_id}/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'x-mas': f'{xmas_value}',
    }
    
    return headers

def headers_season_stats(player_id, season_id):
    api_url = f"/api/playerStats?playerId={player_id}&seasonId={season_id}"
    xmas_value = create_xmas_header(api_url, xmas_pass)
    
    headers = {
        'accept': '*/*',
        'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': f'https://www.fotmob.com/en-GB/players/{player_id}/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'x-mas': f'{xmas_value}',
    }
    
    return headers

def fetch_players(search_term):
    if not search_term or not search_term.strip():
        return {}

    try:
        params = {
            'hits': CONFIG['MAX_HITS'],
            'lang': CONFIG['DEFAULT_LANGUAGE'],
            'term': search_term,
        }

        response = requests.get(
            f'{CONFIG["API_BASE_URL"]}/search/suggest', 
            params=params, 
            headers=CONFIG['HEADERS']
        )
        response.raise_for_status()
        
        data = response.json()
        
        if not isinstance(data, list) or len(data) == 0 or 'suggestions' not in data[0]:
            st.warning(TRANSLATIONS[selected_lang]['player_not_found'])
            return {}

        suggestions = data[0]['suggestions']
        players = {f"{player['name']} ({player['teamName']})": player['id'] 
                  for player in suggestions 
                  if player['type'] == 'player'}
        
        if not players:
            st.warning(TRANSLATIONS[selected_lang]['player_not_found'])
            
        return players

    except Exception as e:
        st.error(f"Arama sırasında hata oluştu: {str(e)}")
        return {}

selected_lang = st.sidebar.selectbox(
    "Language / Dil / Langue",
    options=['en', 'tr', 'fr'],
    format_func=lambda x: {
        'en': 'English',
        'tr': 'Türkçe',
        'fr': 'Français'
    }.get(x, x)
)

search_term = st.sidebar.text_input(
    TRANSLATIONS[selected_lang]['player_search'],
    placeholder=TRANSLATIONS[selected_lang]['player_search_placeholder'],
    help=TRANSLATIONS[selected_lang]['player_search_help']
)

all_players = {}

if not search_term.strip():
    st.sidebar.warning(TRANSLATIONS[selected_lang]['player_empty_warning'])
else:
    players1 = fetch_players(search_term)

    if players1:
        all_players = {**players1}
        
        if 'selected_player' not in st.session_state:
            st.session_state.selected_player = list(all_players.keys())[0]
        if 'selected_season' not in st.session_state:
            st.session_state.selected_season = None

        def on_player_select():
            st.session_state.selected_season = None

        selected_player = st.sidebar.selectbox(
            TRANSLATIONS[selected_lang]['player_selection'],
            options=list(all_players.keys()),
            key='selected_player',
            on_change=on_player_select,
            help=TRANSLATIONS[selected_lang]['player_selection_help']
        )

        player_id = all_players.get(selected_player)
    else:
        st.sidebar.write(TRANSLATIONS[selected_lang]['player_not_found'])
        
def get_player_season_infos(player_id):
    response = requests.get(f'https://www.fotmob.com/api/playerData?id={player_id}', headers=headers(player_id))
    data = response.json()
    return data.get('statSeasons', [])

def select_season_and_league(player_seasons):
    options = []
    option_to_entryid = {}

    for season in player_seasons:
        season_name = season['seasonName']
        for tournament in season['tournaments']:
            display_name = f"{season_name} - {tournament['name']}"
            entry_id = tournament['entryId']
            options.append(display_name)
            option_to_entryid[display_name] = entry_id

    selected_option = st.sidebar.selectbox(
        TRANSLATIONS[selected_lang]['season_league_select'],
        options,
        help=TRANSLATIONS[selected_lang]['season_league_help']
    )
    return option_to_entryid[selected_option]

def get_player_primary_position(player_id):
    response = requests.get(f'https://www.fotmob.com/api/playerData?id={player_id}', headers=headers(player_id))
    data = response.json()
    primary_position = data.get('positionDescription', {}).get('primaryPosition', {}).get('label')
    return primary_position
    
translation_dict = {
    'tr': {
        'Tackles': 'Top Çalma',
        'Duels won': 'Kazanılan İkili Mücadele',
        'Duels won %': 'Kazanılan İkili Mücadele\nYüzdesi',
        'Aerials won': 'Kazanılan Hava Topu',
        'Aerials won %': 'Kazanılan Hava Topu\nYüzdesi',
        'Interceptions': 'Top Kapma',
        'Recoveries': 'Top Kazanma',
        'Accurate passes': 'Başarılı Pas',
        'Pass accuracy': 'Başarılı Pas\nYüzdesi',
        'Successful crosses': 'Başarılı Orta',
        'Cross accuracy': 'Başarılı Orta\nYüzdesi',
        'Accurate long balls': 'Başarılı Uzun Top',
        'Long ball accuracy': 'Başarılı Uzun Top\nYüzdesi',
        'Chances created': 'Gol Şansı Yaratma',
        'Touches': 'Topla Buluşma',
        'Dribbles': 'Başarılı Çalım',
        'Dribbles success rate': 'Başarılı Çalım\nYüzdesi',
        'Saves': 'Kurtarışlar',
        'Save percentage': 'Kurtarış Yüzdesi',
        'Goals prevented': 'Gol Kurtarma',
        'Clean sheets': 'Gol Yemeden\nBitirilen Maçlar',
        'Penalty goals saves': 'Penaltı Kurtarma',
        'Blocked scoring attempt': 'Gol Engelleme',
        'Possession won final 3rd': 'Rakip Alanda\nTop Çalma',
        'Fouls committed': 'Yapılan Faul',
        'Fouls won': 'Kazanılan Faul',
        'Goals': 'Gol',
        'xG': 'Gol Beklentisi (xG)',
        'xGOT': 'İsabetli Şutta xG (xGOT)',
        'xG excl. penalty': 'Penaltısız Gol Beklentisi\n(xGnP)',
        'Shots': 'Şut',
        'Shots on target': 'İsabetli Şut',
        'Assists': 'Asist',
        'xA': 'Asist Beklentisi (xA)',
        'Touches in opposition box': 'Rakip Ceza Sahasında\nTopla Buluşma'
    },
    'fr': {
        'Tackles': 'Tacles',
        'Duels won': 'Duels gagnés',
        'Duels won %': 'Pourcentage de\nduels gagnés',
        'Aerials won': 'Duels aériens gagnés',
        'Aerials won %': 'Pourcentage de\nduels aériens gagnés',
        'Interceptions': 'Interceptions',
        'Recoveries': 'Ballons récupérés',
        'Accurate passes': 'Passes réussies',
        'Pass accuracy': 'Précision des passes',
        'Successful crosses': 'Centres réussis',
        'Cross accuracy': 'Précision des centres',
        'Accurate long balls': 'Longs ballons réussis',
        'Long ball accuracy': 'Précision des\nlongs ballons',
        'Chances created': 'Occasions créées',
        'Touches': 'Touches de balle',
        'Dribbles': 'Dribbles réussis',
        'Dribbles success rate': 'Taux de\nréussite des dribbles',
        'Saves': 'Arrêts',
        'Save percentage': 'Pourcentage d\'arrêts',
        'Goals prevented': 'Buts évités',
        'Clean sheets': 'Matchs sans encaisser',
        'Penalty goals saves': 'Arrêts sur penalty',
        'Blocked scoring attempt': 'Tentative de but bloquée',
        'Possession won final 3rd': 'Ballons récupérés\ndans le dernier tiers',
        'Fouls committed': 'Fautes commises',
        'Fouls won': 'Fautes subies',
        'Goals': 'Buts',
        'xG': 'xG (buts attendus)',
        'xGOT': 'xGOT (xG sur tirs cadrés)',
        'xG excl. penalty': 'xG hors penalty',
        'Shots': 'Tirs',
        'Shots on target': 'Tirs cadrés',
        'Assists': 'Passes décisives',
        'xA': 'xA (passes décisives attendues)',
        'Touches in opposition box': 'Touches dans la surface\nadverse'
    }
}

def translate_stats(stat_titles, lang, translation_dict):
    if lang == 'en':
        return stat_titles
    return [translation_dict.get(lang, {}).get(stat, stat) for stat in stat_titles]

def fetch_player_stats(player_id: int, season_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch player statistics from the API.
    
    Args:
        player_id: The unique identifier of the player
        season_id: The season identifier to fetch stats for
        
    Returns:
        Dictionary containing player stats or None if request fails
    """
    try:
        response = requests.get(
            f'{CONFIG["API_BASE_URL"]}/playerStats',
            params={'playerId': player_id, 'seasonId': season_id},
            headers=headers_season_stats(player_id, season_id)
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch player stats: {str(e)}")
        return None

def create_player_df(player_data):  
    if 'statsSection' not in player_data:
        return pd.DataFrame()
    
    top_stats = player_data['statsSection']['items']
    dfs = [pd.DataFrame(stat['items']).assign(category=stat['title']) for stat in top_stats]
    return pd.concat(dfs, ignore_index=True)

def extract_stat_values(df, stat_titles):
    stat_values = []
    for title in stat_titles:
        value = df.loc[df['title'] == title, 'per90'].values
        if len(value) > 0:
            stat_values.append(round(value[0], 2))
        else:
            stat_values.append(0)
    return stat_values

def extract_stat_values_percentage(df, stat_titles):
    stat_values = []
    for title in stat_titles:
        value = df.loc[df['title'] == title, 'percentileRank'].values
        if len(value) > 0:
            stat_values.append(round(value[0], 2))
        else:
            stat_values.append(0)
    return stat_values

def get_player_name(player_id):
    response = requests.get(f'https://www.fotmob.com/api/playerData?id={player_id}', headers=headers(player_id))
    data = response.json()
    name = data["name"]
    return name

def get_minutes(player_data, specific_stat_name):
    items = player_data['topStatCard']['items']
    
    for item in items:
        if item.get('title') == specific_stat_name:
            return item.get('statValue')
    
    return None

def get_matches_count(player_data, specific_stat_name):
    items = player_data['topStatCard']['items']
    
    for item in items:
        if item.get('title') == specific_stat_name:
            return item.get('statValue')
    
    return None

def get_started_matches_count(player_data, specific_stat_name):
    items = player_data['topStatCard']['items']
    
    for item in items:
        if item.get('title') == specific_stat_name:
            return item.get('statValue')
    
    return None

def fetch_player_season_and_league(data, season_id):
    stat_seasons = data.get('statSeasons', [])
    
    season_text = None
    league_name = None

    for season in stat_seasons:
        tournaments = season.get('tournaments', [])
        for tournament in tournaments:
            entry_id = tournament.get('entryId')
            if entry_id == season_id:
                season_text = season.get('seasonName')
                league_name = tournament.get('name')
                break
        if season_text and league_name:
            break

    return season_text, league_name

def get_birthday(data):
    birthday = data["birthDate"]["utcTime"]

    date_obj = datetime.fromisoformat(birthday.replace("Z", "+00:00"))

    formatted_date = date_obj.strftime("%d.%m.%Y")
    return formatted_date

def get_age(data):
    player_information = data.get('playerInformation', [])
    
    for item in player_information:
        if item.get('title') == 'Age':
            return item['value'].get('numberValue')
    
    return None

def get_player_general_data(player_id):
    try:
        response = requests.get(
            f'{CONFIG["API_BASE_URL"]}/playerData',
            params={'id': player_id},
            headers=headers(player_id)
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch player data: {str(e)}")
        return None

st.markdown("""
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

                    html, body, [class*="cache"], [class*="st-"]  {
                        font-family: 'Poppins', sans-serif;
                    }
                    </style>
                    """, unsafe_allow_html=True
                )

if 'selected_player' in st.session_state and st.session_state.selected_player:
    player_id = all_players.get(st.session_state.selected_player)
    
    if player_id:
        player_name = str(get_player_name(int(player_id)))
        
        player_seasons = get_player_season_infos(player_id)
        
        if player_seasons:
            player_season_id = select_season_and_league(player_seasons)
        else:
            player_season_id = "0-0"
            
        def translate_position(position, lang):
            position_translations = {
                'en': {
                    "Goalkeeper": "Goalkeeper",
                    "Keeper": "Goalkeeper",
                    "Right Back": "Right Back",
                    "Left Back": "Left Back",
                    "Center Back": "Center Back",
                    "Right Wing-Back": "Right Wing-Back",
                    "Left Wing-Back": "Left Wing-Back",
                    "Right Midfielder": "Right Midfielder",
                    "Left Midfielder": "Left Midfielder",
                    "Central Midfielder": "Central Midfielder",
                    "Attacking Midfielder": "Attacking Midfielder",
                    "Defensive Midfielder": "Defensive Midfielder",
                    "Right Winger": "Right Winger",
                    "Left Winger": "Left Winger",
                    "Striker": "Striker",
                    "Forward": "Forward",
                    "Center Forward": "Center Forward"
                },
                'tr': {
                    "Goalkeeper": "Kaleci",
                    "Keeper": "Kaleci",
                    "Right Back": "Sağ Bek",
                    "Left Back": "Sol Bek",
                    "Center Back": "Stoper",
                    "Right Wing-Back": "Sağ Kanat Bek",
                    "Left Wing-Back": "Sol Kanat Bek",
                    "Right Midfielder": "Sağ Orta Saha",
                    "Left Midfielder": "Sol Orta Saha",
                    "Central Midfielder": "Merkez Orta Saha",
                    "Attacking Midfielder": "Ofansif Orta Saha",
                    "Defensive Midfielder": "Defansif Orta Saha",
                    "Right Winger": "Sağ Kanat",
                    "Left Winger": "Sol Kanat",
                    "Striker": "Forvet",
                    "Forward": "Hücumcu",
                    "Center Forward": "Santrafor"
                },
                'fr': {
                    "Goalkeeper": "Gardien de but",
                    "Keeper": "Gardien",
                    "Right Back": "Arrière droit",
                    "Left Back": "Arrière gauche",
                    "Center Back": "Défenseur central",
                    "Right Wing-Back": "Latéral droit offensif",
                    "Left Wing-Back": "Latéral gauche offensif",
                    "Right Midfielder": "Milieu droit",
                    "Left Midfielder": "Milieu gauche",
                    "Central Midfielder": "Milieu central",
                    "Attacking Midfielder": "Milieu offensif",
                    "Defensive Midfielder": "Milieu défensif",
                    "Right Winger": "Ailier droit",
                    "Left Winger": "Ailier gauche",
                    "Striker": "Attaquant",
                    "Forward": "Avant",
                    "Center Forward": "Avant-centre"
                }
            }
            return position_translations.get(lang, position_translations['en']).get(position, position)

        player_primary_position = get_player_primary_position(player_id)
        player_position_translated = translate_position(player_primary_position, selected_lang)
        
        selectbox_index = 0

        if player_primary_position == "Goalkeeper":
            selectbox_index = 0
        if player_primary_position == "Center Back":
            selectbox_index = 1
        if player_primary_position == "Left Back" or player_primary_position == "Right Back" or player_primary_position == "Right Wing-Back" or player_primary_position == "Left Wing-Back":
            selectbox_index = 2
        if player_primary_position == "Defensive Midfielder" or player_primary_position == "Central Midfielder":
            selectbox_index = 3
        if player_primary_position == "Left Winger" or player_primary_position == "Right Winger" or player_primary_position == "Attacking Midfielder" or player_primary_position == "Right Midfielder" or player_primary_position == "Left Midfielder":
            selectbox_index = 4
        if player_primary_position == "Striker":
            selectbox_index = 5
            
        pizza_template = st.sidebar.selectbox(
            TRANSLATIONS[selected_lang]['pizza_template'],
            options=list(TRANSLATIONS[selected_lang]['templates'].values()),
            index=selectbox_index,
            help=TRANSLATIONS[selected_lang]['pizza_template_help']
        )

        def get_template_key(selected_template, lang):
            templates = TRANSLATIONS[lang]['templates']
            for key, value in templates.items():
                if value == selected_template:
                    return key
            return None

        template_key = get_template_key(pizza_template, selected_lang)

        if template_key == "Goalkeeper":
            stat_titles = ["Saves", "Save percentage", "Goals prevented", "Clean sheets", "Penalty goals saves",
                         "Pass accuracy", "Accurate long balls", "Long ball accuracy"]

        if template_key == "Center Back":
            stat_titles = ['Tackles', 'Duels won', 'Duels won %', 'Interceptions', 'Recoveries', 'Blocked scoring attempt',
                         'Accurate passes', 'Accurate long balls',  'Long ball accuracy']

        if template_key == "Right Back - Left Back":
            stat_titles = ['Tackles', 'Duels won', 'Duels won %', 'Interceptions', 'Recoveries',
                         'Accurate passes', 'Chances created', 'Successful crosses', 'Cross accuracy',
                         'Dribbles', 'Touches in opposition box']
            
        if template_key == "Central Midfielder":
            stat_titles = ['Accurate passes', 'Pass accuracy', 'Accurate long balls', 'Long ball accuracy',
                         'Tackles', 'Interceptions', 'Recoveries', 'Duels won', 'Aerials won', 'Possession won final 3rd',
                         'Touches', 'Dribbles']
            
        if template_key == "Winger - Attacking Midfielder":
            stat_titles = ['Goals', 'Shots', 'Shots on target',
                         'Assists', 'Chances created', 'Successful crosses',
                         'Duels won', 'Possession won final 3rd', 'Fouls won',
                         'Dribbles', 'Dribbles success rate']
            
        if template_key == "Striker":
            stat_titles = ['Goals', 'xG excl. penalty', 'Shots', 'Shots on target',
                         'Assists', 'xA', 'Chances created',
                         'Duels won', 'Aerials won', 'Dribbles', 'Possession won final 3rd', 'Fouls won']

        player_stats = fetch_player_stats(int(player_id), player_season_id)
        
        if player_stats != None:
            player_df = create_player_df(player_stats)
            
            player_general_data = get_player_general_data(player_id)
            
            if (len(player_df) >= 15):
                player_age = get_age(player_general_data)

                player_birthday = get_birthday(player_general_data)

                player_matches = get_matches_count(player_stats, 'Matches')

                player_started_matches = get_started_matches_count(player_stats, 'Started')
                
                minute_str = get_minutes(player_stats, 'Minutes')

                if minute_str is not None:
                    player_minute = int(minute_str)
                else:
                    player_minute = None
            
                player_bos_mu = player_df.empty or isinstance(player_df, pd.DataFrame) and player_df.shape == (0, 0)
                
                if not player_bos_mu:
                    df_stat_values = extract_stat_values(player_df, stat_titles)
                    df_stat_values_percentage = extract_stat_values_percentage(player_df, stat_titles)
                    
                    player_season_name, player_league = fetch_player_season_and_league(player_general_data, player_season_id)
                    
                    def get_team_name_from_season_and_league(data, season_string, league_string):
                        def season_matches(season_name, season_string):
                            season_parts = season_name.split('/')
                            if '/' in season_string:
                                for part in season_parts:
                                    if part.strip() in season_string.split('/'):
                                        return True
                            else:
                                if season_string in season_parts or season_name == season_string:
                                    return True
                            return False
                        
                        if 'senior' in data['careerHistory']['careerItems']:
                            for season in data['careerHistory']['careerItems']['senior']['seasonEntries']:
                                if season['seasonName'] == season_string:
                                    for tournament in season['tournamentStats']:
                                        if tournament['leagueName'] == league_string:
                                            return season['team'], season['teamId']
                        
                        if 'national team' in data['careerHistory']['careerItems']:
                            for season in data['careerHistory']['careerItems']['national team']['seasonEntries']:
                                if season_matches(season['seasonName'], season_string):
                                    for tournament in season['tournamentStats']:
                                        if tournament['leagueName'] == league_string:
                                            return season['team'], season['teamId']
                        
                        return None, None
                    
                    player_team, player_team_id = get_team_name_from_season_and_league(player_general_data, player_season_name, player_league)
                    
                    if selected_lang == 'en':
                        chart_stat_titles = stat_titles
                        minute_string = "Minutes"
                        data_string = "Data"
                    elif selected_lang == 'tr':
                        chart_stat_titles = translate_stats(stat_titles, 'tr', translation_dict)
                        minute_string = "Dakika"
                        data_string = "Veri"
                    elif selected_lang == 'fr':
                        chart_stat_titles = translate_stats(stat_titles, 'fr', translation_dict)
                        minute_string = "Minutes"
                        data_string = "Données"
                    
                    plot = create_pizza_chart(
                        df_stat_values,
                        df_stat_values_percentage,
                        chart_stat_titles,
                        player_name,
                        player_id,
                        player_team_id,
                        player_league,
                        player_season_name,
                        player_position_translated,
                        player_minute,
                        minute_string,
                        data_string,
                        background_color="#0e0e0e",
                        main_color="#0e346d"
                    )
                    
                    st.pyplot(plot)
                
                    st.markdown("""
                        <style>
                        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

                        html, body, [class*="cache"], [class*="st-"]  {
                            font-family: 'Poppins', sans-serif;
                        }
                        </style>
                        """, unsafe_allow_html=True
                    )
                    
                    st.markdown(
                        """
                        <style>
                            /* Bilgisayarlar için */
                            @media (min-width: 1024px) {
                                .block-container {
                                    width: 700px;
                                    max-width: 700px;
                                    padding-top: 25px;
                                    padding-bottom: 0px;
                                }
                            }

                            /* Tabletler için (genellikle 768px - 1024px arası ekran genişliği) */
                            @media (min-width: 768px) and (max-width: 1023px) {
                                .block-container.st-emotion-cache-13ln4jf.ea3mdgi5 {
                                    width: 500px;
                                    max-width: 500px;
                                }
                            }

                            /* Telefonlar için (genellikle 768px ve altı ekran genişliği) */
                            @media (max-width: 767px) {
                                .block-container.st-emotion-cache-13ln4jf.ea3mdgi5 {
                                    width: 100%;
                                    max-width: 100%;
                                    padding-left: 10px;
                                    padding-right: 10px;
                                }
                            }
                            .stDownloadButton {
                                display: flex;
                                justify-content: center;
                                text-align: center;
                            }
                            .stDownloadButton button {
                                background-color: rgba(51, 51, 51, 0.17);
                                color: gray;  /* Text color */
                                border: 0.5px solid gray;  /* Thin gray border */
                                transition: background-color 0.5s ease;
                            }
                            .stDownloadButton button:hover {
                                background-color: rgba(51, 51, 51, 0.65);
                                border: 1px solid gray;  /* Thin gray border */
                                color: gray;  /* Text color */
                            }
                            .stDownloadButton button:active {
                                background-color: rgba(51, 51, 51, 0.17);
                                color: gray;  /* Text color */
                                border: 0.5px solid gray;  /* Thin gray border */
                                transition: background-color 0.5s ease;
                            }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    buf = io.BytesIO()
                    plot.savefig(buf, format="png", dpi = 300, bbox_inches = "tight")
                    buf.seek(0)
                    player_name_clean = player_name.replace(" ", "-")
                    player_league_clean = player_league.replace(" ", "-")
                    
                    st.download_button(
                        label=TRANSLATIONS[selected_lang]['download_button'],
                        data=buf,
                        file_name=f"{player_name_clean}-{player_season_name}-{player_league_clean}.png",
                        mime="image/png"
                    )
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    st.markdown(
                        f"""
                        <div style='text-align: center; max-width:550px; margin: 0 auto; cursor:default; margin-bottom: 50px;'>
                            <p style='font-size:12px; color:gray;'>{TRANSLATIONS[selected_lang]['info_text']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.write(TRANSLATIONS[selected_lang]['no_player_data'])        
        else:
            st.write(TRANSLATIONS[selected_lang]['no_player_data'])
    #else:
            #st.write(TRANSLATIONS[selected_lang]['no_player_data'])

def load_player_data(player_id: int, season_id: str):
    with st.spinner('Oyuncu verileri yükleniyor...'):
        try:
            stats = fetch_player_stats(player_id, season_id)
            if not stats:
                st.error("Oyuncu istatistikleri alınamadı.")
                return None
                
            general_data = get_player_general_data(player_id)
            if not general_data:
                st.error("Oyuncu genel bilgileri alınamadı.")
                return None
                
            return stats, general_data
            
        except Exception as e:
            st.error(f"Veri yüklenirken hata oluştu: {str(e)}")
            return None

def img_to_base64(img_path):
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

st.sidebar.markdown("---")  

twitter_icon_base64 = img_to_base64("icons/twitter.png")
github_icon_base64 = img_to_base64("icons/github.png")
twitter_icon_white_base64 = img_to_base64("icons/twitter_white.png")
github_icon_white_base64 = img_to_base64("icons/github_white.png") 

st.sidebar.markdown(
    f"""
    <style>
    .sidebar {{
        width: auto;
    }}
    .sidebar-content {{
        display: flex;
        flex-direction: column;
        height: 100%;
        margin-top: 10px;
    }}
    .icon-container {{
        display: flex;
        justify-content: center;
        margin-top: auto;
        padding-bottom: 20px;
        gap: 30px;  /* Space between icons */
    }}
    .icon-container img {{
        transition: filter 0.5s cubic-bezier(0.4, 0, 0.2, 1);  /* Smooth and natural easing */
    }}
    .icon-container a:hover img {{
        filter: brightness(0) invert(1);  /* Inverts color to white */
    }}
    </style>
    <div class="sidebar-content">
        <!-- Other sidebar content like selectbox goes here -->
        <div class="icon-container">
            <a href="https://x.com/bariscanyeksin" target="_blank">
                <img src="data:image/png;base64,{twitter_icon_base64}" alt="Twitter" width="30">
            </a>
            <a href="https://github.com/bariscanyeksin" target="_blank">
                <img src="data:image/png;base64,{github_icon_base64}" alt="GitHub" width="30">
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)





