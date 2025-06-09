import flet as ft
from datetime import datetime
import random
import math 
import time
import threading # <-- AQUÍ ESTÁ LA LÍNEA QUE FALTABA

# --- ESTADO DEL CLIMA ---
current_weather_state = 'Soleado' 

# Datos simulados por sensor
sensor_data = {
    "DHT22": {"temp": 5.0, "hum": 45.0},
    "BME280": {"temp": 4.8, "pres": 1018},
    "BH1750": {"lux": 15000},
    "YL-83": {"rain": False},
    "Viento": {"vel": 10, "dir": "W"},
}

# Histórico para gráficos
history = { "temp": [], "hum": [], "pres": [], "lux": [], "vel": [] }

# Alertas
alerts = []

def simulate_sensor_reading():
    global current_weather_state
    new_alert_added = False

    # 1. Lógica de Transición de Estados Climáticos
    if random.random() < 0.5:
        if current_weather_state == 'Soleado': current_weather_state = 'Nublado'
        elif current_weather_state == 'Nublado': current_weather_state = random.choice(['Soleado', 'Lluvioso'])
        elif current_weather_state == 'Lluvioso': current_weather_state = random.choice(['Nublado', 'Tormenta'])
        elif current_weather_state == 'Tormenta': current_weather_state = 'Lluvioso'

    # 2. Lógica de Día/Noche
    hora_actual = datetime.now().hour
    is_daytime = 9 < hora_actual < 18 

    # 3. Lógica de Eventos Climáticos Extremos
    evento_extremo = None
    if random.random() < 0.5: 
        evento_extremo = random.choice(['ola_calor', 'ola_frio'])

    if evento_extremo == 'ola_calor':
        current_weather_state = 'Soleado' 
        sensor_data["DHT22"]["temp"] = round(random.uniform(20.1, 22.0), 1)
        sensor_data["DHT22"]["hum"] = round(random.uniform(20, 30), 1)
    elif evento_extremo == 'ola_frio':
        sensor_data["DHT22"]["temp"] = round(random.uniform(-12.0, -10.1), 1)
        sensor_data["DHT22"]["hum"] = round(random.uniform(40, 50), 1)

    if evento_extremo is None:
        if current_weather_state == 'Soleado':
            sensor_data["DHT22"]["temp"] = round(max(-10, min(30, sensor_data["DHT22"]["temp"] + random.uniform(-0.2, 0.2))), 1)
            sensor_data["DHT22"]["hum"] = round(max(30, min(55, sensor_data["DHT22"]["hum"] + random.uniform(-1, 1))), 1)
            sensor_data["BME280"]["pres"] = round(max(1015, min(1025, sensor_data["BME280"]["pres"] + random.uniform(-0.5, 0.5))), 1)
            sensor_data["Viento"]["vel"] = max(0, min(15, sensor_data["Viento"]["vel"] + random.uniform(-1, 1)))
            sensor_data["BH1750"]["lux"] = random.randint(20000, 50000) if is_daytime else 0
            sensor_data["YL-83"]["rain"] = False
        elif current_weather_state == 'Nublado':
            sensor_data["DHT22"]["temp"] = round(max(-5, min(5, sensor_data["DHT22"]["temp"] + random.uniform(-0.2, 0.2))), 1)
            sensor_data["DHT22"]["hum"] = round(max(50, min(75, sensor_data["DHT22"]["hum"] + random.uniform(-1, 1))), 1)
            sensor_data["BME280"]["pres"] = round(max(1005, min(1015, sensor_data["BME280"]["pres"] + random.uniform(-0.5, 0.5))), 1)
            sensor_data["Viento"]["vel"] = max(5, min(28, sensor_data["Viento"]["vel"] + random.uniform(-2, 2)))
            sensor_data["BH1750"]["lux"] = random.randint(1000, 10000) if is_daytime else 0
            sensor_data["YL-83"]["rain"] = False
        elif current_weather_state == 'Lluvioso':
            sensor_data["DHT22"]["temp"] = round(max(0, min(4, sensor_data["DHT22"]["temp"] + random.uniform(-0.1, 0.1))), 1)
            sensor_data["DHT22"]["hum"] = round(max(70, min(95, sensor_data["DHT22"]["hum"] + random.uniform(-1, 1))), 1)
            sensor_data["BME280"]["pres"] = round(max(995, min(1005, sensor_data["BME280"]["pres"] + random.uniform(-1, 0.5))), 1)
            sensor_data["Viento"]["vel"] = max(15, min(35, sensor_data["Viento"]["vel"] + random.uniform(-2, 2)))
            sensor_data["BH1750"]["lux"] = random.randint(100, 1000) if is_daytime else 0
            sensor_data["YL-83"]["rain"] = True
        elif current_weather_state == 'Tormenta':
            sensor_data["DHT22"]["temp"] = round(max(0, min(3, sensor_data["DHT22"]["temp"] + random.uniform(-0.1, 0.1))), 1)
            sensor_data["DHT22"]["hum"] = round(max(85, min(100, sensor_data["DHT22"]["hum"] + random.uniform(-0.5, 0.5))), 1)
            sensor_data["BME280"]["pres"] = round(max(980, min(995, sensor_data["BME280"]["pres"] + random.uniform(-1.5, -0.5))), 1)
            sensor_data["Viento"]["vel"] = max(25, min(50, sensor_data["Viento"]["vel"] + random.uniform(1, 5)))
            sensor_data["BH1750"]["lux"] = random.randint(50, 500) if is_daytime else 0
            sensor_data["YL-83"]["rain"] = True
    
    sensor_data["BME280"]["temp"] = sensor_data["DHT22"]["temp"] - random.uniform(0.1, 0.3)
    sensor_data["Viento"]["dir"] = random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"])

    # 4. Generación Centralizada de Alertas Visuales
    if sensor_data["DHT22"]["temp"] < -10:
        if not alerts or "BAJA" not in alerts[-1][0]:
            alerts.append(("❄️ Temp. PELIGROSAMENTE BAJA", "#003ab6"))
            new_alert_added = True
    if sensor_data["DHT22"]["temp"] > 20:
        if not alerts or "ALTA" not in alerts[-1][0]:
            alerts.append(("🌡️ Temp. INUSUALMENTE ALTA", "#ff6600"))
            new_alert_added = True
    if sensor_data["YL-83"]["rain"]:
        if not alerts or "lloviendo" not in alerts[-1][0]:
            alerts.append(("🌧️ ¡Está lloviendo!", "#4ebef3ff"))
            new_alert_added = True
    if sensor_data["Viento"]["vel"] > 30:
        if not alerts or "VIENTOS" not in alerts[-1][0]:
             alerts.append(("🌪️ VIENTOS FUERTES", "#6f0f92"))
             new_alert_added = True
    
    # 5. Agregar datos al historial
    for key in history:
        if len(history[key]) > 20: history[key].pop(0)
    history["temp"].append(sensor_data["DHT22"]["temp"])
    history["hum"].append(sensor_data["DHT22"]["hum"])
    history["pres"].append(sensor_data["BME280"]["pres"])
    history["lux"].append(sensor_data["BH1750"]["lux"])
    history["vel"].append(sensor_data["Viento"]["vel"])
    return new_alert_added

def data_card(title, emoji, value, unit, color1, color2, is_alert=False):
    return ft.Container(
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8,
            controls=[
                ft.Text(emoji, size=34), ft.Text(title, color="white70", size=14),
                ft.Text(f"{value} {unit}", weight=ft.FontWeight.BOLD, size=26, color="white"),
            ],
        ),
        width=170, height=170, border_radius=35,
        gradient=ft.LinearGradient(begin=ft.alignment.top_left, end=ft.alignment.bottom_right, colors=[color1, color2]),
        shadow=ft.BoxShadow(spread_radius=6, blur_radius=30, color="#38000000", offset=ft.Offset(0, 8)),
        animate=ft.Animation(500, "bounceOut") if is_alert else None,
        border=ft.border.all(3, "#ff0000") if is_alert else None
    )

def create_chart(data, line_color, title):
    if not data:
        data_points_for_chart, min_y_val, max_y_val = [ft.LineChartDataPoint(0, 0)], -1, 1
    else:
        data_points_for_chart = [ft.LineChartDataPoint(i, val) for i, val in enumerate(data)]
        min_val, max_val = min(data), max(data)
        if len(data) == 1 or min_val == max_val:
            min_y_val, max_y_val = min_val - 0.5, max_val + 0.5
        else:
            padding = (max_val - min_val) * 0.1
            if padding == 0: padding = 0.5
            min_y_val, max_y_val = min_val - padding, max_val + padding
        if min_y_val >= max_y_val: max_y_val = min_y_val + 1

    return ft.Column(controls=[
        ft.Text(title, color="white70", size=12),
        ft.LineChart(
            data_series=[ft.LineChartData(data_points=data_points_for_chart, color=line_color, stroke_width=3, curved=True)],
            border=ft.border.all(1, "#37474f"), left_axis=ft.ChartAxis(labels_size=40, show_labels=True),
            bottom_axis=ft.ChartAxis(labels_size=0, show_labels=False), tooltip_bgcolor="#CC121212", 
            min_y=min_y_val, max_y=max_y_val, expand=True, height=150
        )], spacing=5
    )

def main(page: ft.Page):
    page.title, page.theme_mode, page.bgcolor, page.padding, page.scroll = ("SCADA Estación Meteorológica", ft.ThemeMode.DARK, "#0f172a", 30, ft.ScrollMode.AUTO)
    
    temp_card, hum_card, pres_card, luz_card, lluvia_card, viento_card = (ft.Column() for _ in range(6))
    alert_container, charts_container = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO, height=150), ft.Column(spacing=20)
    
    reloj = ft.Column(
    spacing=2,
    controls=[
        ft.Text(datetime.now().strftime("%A, %B %d"), 
               size=18, 
               weight=ft.FontWeight.W_500,
               text_align=ft.TextAlign.CENTER),  # Centrado horizontal
        ft.Text(datetime.now().strftime("%H:%M"), 
               size=28, 
               weight=ft.FontWeight.W_600,
               text_align=ft.TextAlign.CENTER)   # Centrado horizontal
    ],
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Centrado del column
    alignment=ft.MainAxisAlignment.CENTER,             # Centrado vertical
    expand=True  # Ocupa todo el espacio disponible
)
    
    def play_alert_sound_effect():
        return ft.Container(width=0, height=0, content=ft.Text("🔔", size=1), animate_opacity=ft.Animation(1000, "easeOut"), opacity=0)

    def update_ui(e=None):
        new_alert_generated = simulate_sensor_reading()
        temp, hum, pres, lux, rain, vel, dir_viento = (sensor_data["DHT22"]["temp"], sensor_data["DHT22"]["hum"], sensor_data["BME280"]["pres"], sensor_data["BH1750"]["lux"], sensor_data["YL-83"]["rain"], sensor_data["Viento"]["vel"], sensor_data["Viento"]["dir"])

        temp_alert, hum_alert, wind_alert, rain_alert = (temp > 20 or temp < -10, hum > 95, vel > 30, rain)

        temp_card.controls = [data_card("Temp DHT22", "🌡️", temp, "°C", "#f90808", "#0056d6", temp_alert)]
        hum_card.controls = [data_card("Humedad", "💧", hum, "%", "#a0d0ea", "#2980b9", hum_alert)]
        pres_card.controls = [data_card("Presión", "🌬️", pres, "hPa", "#96a3a9", "#607d8b")]
        luz_card.controls = [data_card("Luz", "💡", lux, "lux", "#ff5100", "#fdd835")]
        lluvia_card.controls = [data_card("Lluvia", "🌧️" if rain else "☀️", "Sí" if rain else "No", "", "#0000f7", "#0288d1", rain_alert)]
        viento_card.controls = [data_card("Viento", "🍃", vel, f"km/h {dir_viento}", "#a8edea", "#fed6e3", wind_alert)]

        alert_controls = []
        for text, alert_color_hex in alerts[-3:]:
            bg_color_with_opacity = f"#33{alert_color_hex.lstrip('#')}"
            alert_controls.append(ft.Container(
                content=ft.Row(controls=[ft.Icon(name="warning_amber_rounded", color=alert_color_hex), ft.Text(text, color="white", weight=ft.FontWeight.BOLD)], spacing=10),
                bgcolor=bg_color_with_opacity, padding=10, border_radius=10, animate_opacity=ft.Animation(500, "easeOut")
            ))
        alert_container.controls = alert_controls

        charts_container.controls = [
            create_chart(history["temp"], "#ef5807", "Temperatura (°C)"),
            create_chart(history["hum"], "#2980b9", "Humedad (%)"),
            create_chart(history["vel"], "#5e81daff", "Velocidad Viento (km/h)")
        ]
        
        reloj.controls[0].value = datetime.now().strftime("%A, %B %d")
        reloj.controls[1].value = datetime.now().strftime("%H:%M")

        if new_alert_generated:
            sound_indicator = play_alert_sound_effect()
            page.add(sound_indicator)
            def animate_sound(indicator):
                indicator.opacity = 1
                if page.controls: page.update()
                time.sleep(0.05)
                indicator.opacity = 0
                if page.controls: page.update()
            threading.Thread(target=animate_sound, args=(sound_indicator,)).start()
        if page.controls: page.update()

    page.add(ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=25,
        controls=[
            ft.Text("🛰️ SCADA - Estación Meteorológica", size=28, weight=ft.FontWeight.BOLD, color="white"),reloj,
            ft.Text("⚠️ ALERTAS", size=16, color="white70"), alert_container,
            ft.Row([temp_card, hum_card, pres_card], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            ft.Row([luz_card, lluvia_card, viento_card], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            ft.Text("📊 HISTORIAL", size=16, color="white70"), charts_container,
        ]
    ))
    
    def auto_update_loop():
        while True:
            time.sleep(2)
            try:
                if page and page.controls: update_ui()
            except Exception as e:
                print(f"Error en auto_update_loop: {e}")
                pass 
    update_thread = threading.Thread(target=auto_update_loop, daemon=True)
    update_thread.start()
    update_ui()

ft.app(target=main)