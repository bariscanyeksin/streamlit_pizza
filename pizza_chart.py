import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib import font_manager as fm
from urllib.request import urlopen
from urllib.error import HTTPError
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image

plt.rcParams['figure.dpi'] = 300
current_dir = os.path.dirname(os.path.abspath(__file__))

# Poppins fontunu yükleme
font_path = os.path.join(current_dir, 'fonts', 'Poppins-Regular.ttf')
prop = fm.FontProperties(fname=font_path)

bold_font_path = os.path.join(current_dir, 'fonts', 'Poppins-SemiBold.ttf')
bold_prop = fm.FontProperties(fname=bold_font_path)

def blend_colors(color1, color2, ratio):
    """
    İki rengi verilen orana göre karıştır.
    
    Args:
        color1: İlk renk (hex string)
        color2: İkinci renk (hex string)
        ratio: Karışım oranı (0-1 arası, 1 olursa tamamen color1)
    """
    # Hex renkleri RGB'ye çevir
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # RGB renkleri karıştır
    c1 = hex_to_rgb(color1)
    c2 = hex_to_rgb(color2)
    
    # Lineer interpolasyon
    blend = tuple(int(c1[i] * ratio + c2[i] * (1 - ratio)) for i in range(3))
    
    # RGB'yi hex'e çevir
    return '#{:02x}{:02x}{:02x}'.format(*blend)

def fetch_player_image(player_id):
    url = f'https://images.fotmob.com/image_resources/playerimages/{player_id}.png'
    try:
        # Resmi indirin
        response = urlopen(url)
        # Resmi açın ve RGBA formatına dönüştürün
        image = Image.open(response).convert('RGBA')
        return image
    except HTTPError as e:
        # HTTPError (403 ve diğer hatalar) durumunda, hata mesajını yazdırın ve None döndürün
        if e.code == 403:
            print(f"403 hatası: {player_id} için fotoğraf bulunamadı.")
        else:
            print(f"HTTPError: {e}")
        return None
    
def fetch_team_logo(team_id):
    url = f'https://images.fotmob.com/image_resources/logo/teamlogo/{team_id}.png'
    try:
        # Resmi indirin
        response = urlopen(url)
        # Resmi açın ve RGBA formatına dönüştürün
        image = Image.open(response).convert('RGBA')
        return image
    except HTTPError as e:
        # HTTPError (403 ve diğer hatalar) durumunda, hata mesajını yazdırın ve None döndürün
        if e.code == 403:
            print(f"403 hatası: {team_id} için fotoğraf bulunamadı.")
        else:
            print(f"HTTPError: {e}")
        return None

def create_pizza_chart(values, values_perc, params, player_name, player_id, team_id, league_name, season_name, position, minute, minute_string, data_string, background_color="white", main_color="#212e47", label_color="gray"):
    """
    Create a pizza chart with separate slices for each statistic.
    
    Args:
        values: List of values for each parameter
        params: List of parameter names
        title: Chart title
        background_color: Color of the background
        main_color: Main color for the slices
    """
    
    # Figür oluştur
    fig = plt.figure(figsize=(12, 12), facecolor=background_color)
    ax = fig.add_subplot(111, projection='polar')
    ax.set_facecolor(background_color)
    
    # Dilim sayısı ve açıları hesapla
    N = len(params)  # 14 dilim
    
    # Hem grid hem de barlar için aynı açıları kullanalım
    theta = np.linspace(0, 2*np.pi, N, endpoint=False)  # N eşit parçaya böl
    width = (2*np.pi) / N  # Her dilimin genişliği
    
    # Grid çizgileri için açıları ayarla
    ax.set_xticks(theta)  # Grid çizgileri dilim başlangıçlarına denk gelsin
    
    ax.set_theta_direction(-1)  # Saat yönünde
    ax.set_theta_zero_location('N')
    
    # Her bir dilimi çiz
    for idx, (angle, value) in enumerate(zip(theta, values_perc)):
        
        # Değere göre karışım oranını hesapla (0.2 ile 1 arasında)
        ratio = 0 + (value / 100) * 0.8
        slice_color = blend_colors(main_color, '#000000', ratio)
        
        # Dilimi çiz
        ax.bar(angle,
              value, 
              width=width,
              color=slice_color,
              edgecolor='white',
              linewidth=1,
              align='edge')
    
    # Izgara ayarları
    ax.set_ylim(0, 100)
    grid_values = [20, 40, 60, 80, 100]
    ax.set_yticks(grid_values)
    
    # Grid çemberlerini doldur
    for i in range(len(grid_values)):
        # Her bir grid çemberi için dolgu
        ax.fill_between(np.linspace(0, 2*np.pi, 100), 
                       grid_values[i], 
                       grid_values[i-1] if i > 0 else 0,
                       color="#cfddfc",
                       alpha=0.05)
    
    # Grid çizgileri
    ax.grid(True, color='gray', alpha=0.3, linestyle='--')

    # İsimleri dışarıya yerleştir
    for idx, (angle, param) in enumerate(zip(theta, params)):
        # Dilimin ortasındaki açıyı hesapla
        center_angle = angle + (width/2)  # Dilimin tam ortası
        rotation_deg = np.degrees(center_angle)
        
        # Açı ve hizalama ayarları - saat yönüne göre düzeltildi
        if 270 <= rotation_deg <= 360 or 0 <= rotation_deg < 90:
            # Sağ yarı
            label_rotation = -rotation_deg
            ha = 'center'
            va = 'center'
        else:
            # Sol yarı (90 <= rotation_deg < 270)
            label_rotation = 180 - rotation_deg
            ha = 'center'
            va = 'center'
        
        # İsmi dışarıya yerleştir
        ax.text(center_angle,   # Dilimin ortasına yerleştir
               107.5,            # Sabit uzaklık
               param, 
               rotation=label_rotation,
               ha=ha,          # Sağ/sol hizalama açıya göre değişir
               va=va,          # Dikey hizalama hep ortada
               color=label_color,
               fontsize=14,
               fontproperties=prop)  # Normal Poppins
    
    # Değer etiketleri
    for idx, (angle, value_perc, value) in enumerate(zip(theta, values_perc, values)):
        # Dilimin ortasındaki açıyı hesapla
        center_angle = angle + (width/2)  # Dilimin tam ortası
        rotation_deg = np.degrees(center_angle)
        
        # Değerin pozisyonunu ayarla - yüzdelik değeri kullan
        r = value_perc  # Bar yüksekliği yüzdelik değere göre
        
        # Açı ve hizalama ayarları - saat yönüne göre düzeltildi
        if 270 <= rotation_deg <= 360 or 0 <= rotation_deg < 90:
            # Sağ yarı
            label_rotation = -rotation_deg
            ha, va = 'center', 'center'
        else:
            # Sol yarı (90 <= rotation_deg < 270)
            label_rotation = 180 - rotation_deg
            ha, va = 'center', 'center'
            
        # Renk hesapla - yüzdelik değere göre
        ratio = 0 + (value_perc / 100) * 0.8
        slice_color = blend_colors(main_color, '#000000', ratio)
            
        # Değer etiketini ekle - gerçek değeri göster
        ax.text(
            center_angle,   # Dilimin tam ortasına yerleştir
            r,             # y pozisyonu (yüzdelik değer)
            f'{value:.2f}',  # Gerçek değeri 2 ondalık basamakla göster
            color='white',
            ha=ha,
            va=va,
            rotation=label_rotation,
            fontsize=10,
            fontproperties=bold_prop,  # Kalın Poppins
            bbox=dict(
                facecolor=slice_color,
                edgecolor="white",
                pad=3,
                boxstyle='round,pad=0.5'
            )
        )
    
    # Eksenleri gizle
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    plt.grid(True, color='gray', alpha=0.3, linestyle='--')
    
    # Diğer elementleri bu axes'in üzerine yerleştir
    title_ax = fig.add_axes([0.22, 1, 0.3, 0.1])
    title_ax.set_facecolor('none')
    title_ax.set_xticklabels([])
    title_ax.set_yticklabels([])
    title_ax.axis('off')
    
    # Alt bilgi
    title_ax.text(0, 0.65,
             player_name,
             size=30, 
             ha="left", 
             va="center",
             color="white",
             fontproperties=bold_prop)
    
    subtitle_text = f"{position} - {league_name} {season_name}"
    
    title_ax.text(0, 0.35,
             subtitle_text,
             size=15, 
             ha="left", 
             va="center",
             color=label_color,
             fontproperties=prop)
    
    if minute == None:
        min_90s = ""
        subtitle_2_text = ""
    else:
        min_90s = minute / 90
        subtitle_2_text = f"{minute} {minute_string} - {min_90s:.1f} 90s'"
    
    title_ax.text(0, 0.1,
             subtitle_2_text,
             size=12, 
             ha="left", 
             va="center",
             color=label_color,
             fontproperties=prop)
    
    player_photo_ax = fig.add_axes([0.1, 1, 0.1, 0.1])  # [sol, alt, genişlik, yükseklik]
    player_photo_ax.set_facecolor('none')
    player_photo_ax.axis('off')
    
    player1_foto = fetch_player_image(player_id)

    if player1_foto:
        # player1_foto'yu kullan
        imagebox1 = OffsetImage(player1_foto, zoom=0.5, interpolation='hanning')
        ab1 = AnnotationBbox(imagebox1, (0.5,0.5), frameon=False, xycoords='axes fraction')
        player_photo_ax.add_artist(ab1)
        pass
    else:
        pass
    
    team_logo_ax = fig.add_axes([0.825, 1, 0.1, 0.1])  # [sol, alt, genişlik, yükseklik]
    team_logo_ax.set_facecolor('none')
    team_logo_ax.axis('off')
    
    team_logo = fetch_team_logo(team_id)
    if team_logo:
        imagebox2 = OffsetImage(team_logo, zoom=0.45, interpolation='hanning')
        ab2 = AnnotationBbox(imagebox2, (0.5,0.45), frameon=False, xycoords='axes fraction')
        team_logo_ax.add_artist(ab2)
        pass
    else:
        pass
    
    # Alt padding için boş bir axes ekle
    padding_bottom_ax = fig.add_axes([0.4, -0.02, 0.2, 0])  # [sol, alt, genişlik, yükseklik]
    padding_bottom_ax.set_facecolor('none')
    padding_bottom_ax.axis('off')
    
    # Üst padding için boş bir axes ekle
    padding_top_ax = fig.add_axes([0.4, 1.12, 0.2, 0])  # [sol, alt, genişlik, yükseklik]
    padding_top_ax.set_facecolor('none')
    padding_top_ax.axis('off')
    
    # Endnote için axes - en altta ve ortada
    endnote_ax = fig.add_axes([0.41, 0, 0.2, 0.05])  # [sol, alt, genişlik, yükseklik]
    endnote_ax.set_facecolor('none')
    #endnote_ax.secondary_xaxis('top')
    endnote_ax.set_xticklabels([])
    endnote_ax.set_yticklabels([])
    endnote_ax.axis('off')
    
    # Alt bilgi - tam ortada
    endnote_ax.text(0.5, 0.5,
             f"{data_string}: FotMob\n@bariscanyeksin",
             size=12, 
             ha="center",  # Yatayda ortala
             va="center",  # Dikeyde en alta yasla
             color=label_color,
             fontproperties=prop)
    
    # Header separator line
    #header_line_ax = fig.add_axes([0.165, 0.96, 0.7, 0.002])  # [sol, alt, genişlik, yükseklik]
    header_line_ax = fig.add_axes([0.1, 0.96, 0.83, 0.002])  # [sol, alt, genişlik, yükseklik]
    header_line_ax.set_facecolor('none')
    header_line_ax.axis('off')
    
    # Yatay çizgi çiz
    header_line_ax.axhline(y=0.5, 
                          color=label_color,  # label_color ile aynı renk
                          alpha=0.8,  # Hafif transparent
                          linewidth=1,  # İnce çizgi
                          linestyle='-')  # Düz çizgi
    
    return plt

