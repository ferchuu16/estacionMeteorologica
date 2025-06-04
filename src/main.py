import flet as ft
from datetime import datetime
import random
import math 
import time

# Datos simulados por sensor
sensor_data = {
    "DHT22": {"temp": 22.5, "hum": 48.0},
    "BME280": {"temp": 22.2, "pres": 1013},
    "BH1750": {"lux": 300},
    "YL-83": {"rain": False},
    "Viento": {"vel": 12, "dir": "NE"},
}

# Histórico para gráficos
history = {
    "temp": [],
    "hum": [],
    "pres": [],
    "lux": [],
    "vel": []
}

# Alertas
alerts = []

# Simular datos dinámicos con posibles problemas
def simulate_sensor_reading():
    new_alert_added = False 
    has_problem = random.random() < 0.1
    
    sensor_data["DHT22"]["temp"] = round(sensor_data["DHT22"]["temp"] + random.uniform(-0.5, 0.5), 1)
    sensor_data["DHT22"]["hum"] = round(max(0, min(100, sensor_data["DHT22"]["hum"] + random.uniform(-1, 1))), 1) 
    sensor_data["BME280"]["temp"] = round(sensor_data["BME280"]["temp"] + random.uniform(-0.5, 0.5), 1)
    sensor_data["BME280"]["pres"] = round(sensor_data["BME280"]["pres"] + random.uniform(-1, 1), 1)
    sensor_data["BH1750"]["lux"] = max(0, int(sensor_data["BH1750"]["lux"] + random.uniform(-20, 20))) 
    sensor_data["YL-83"]["rain"] = random.choice([True, False])
    current_vel = sensor_data["Viento"]["vel"]
    change = random.randint(-2,2)
    # Evitar que la velocidad baje mucho de golpe o se vuelva negativa fácilmente
    if current_vel + change < 0 and current_vel > 5 : # Si va a bajar mucho y no estaba cerca de 0
        sensor_data["Viento"]["vel"] = max(0, current_vel + random.randint(-1,1)) # Cambio más suave
    else:
        sensor_data["Viento"]["vel"] = max(0, current_vel + change)

    if sensor_data["Viento"]["vel"] > 40 : sensor_data["Viento"]["vel"] = random.randint(5,25) # Reset si es muy alto

    sensor_data["Viento"]["dir"] = random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"])

    if has_problem:
        problem_type = random.choice(["temp_high", "temp_low", "hum_high", "hum_low", "wind_high"])
        if problem_type == "temp_high":
            sensor_data["DHT22"]["temp"] = round(40 + random.uniform(0, 5),1)
            alerts.append(("🌡️ Temperatura PELIGROSAMENTE ALTA", "#ff0000"))
            new_alert_added = True
        elif problem_type == "temp_low":
            sensor_data["DHT22"]["temp"] = round(-5 + random.uniform(-2, 2),1)
            alerts.append(("❄️ Temperatura PELIGROSAMENTE BAJA", "#00b4d8"))
            new_alert_added = True
        elif problem_type == "hum_high":
            sensor_data["DHT22"]["hum"] = round(95 + random.uniform(0, 5),1)
            alerts.append(("💧 Humedad EXCESIVA", "#0096c7"))
            new_alert_added = True
        elif problem_type == "hum_low":
            sensor_data["DHT22"]["hum"] = round(10 + random.uniform(-5, 5),1)
            alerts.append(("🏜️ Humedad MUY BAJA", "#ff9500"))
            new_alert_added = True
        elif problem_type == "wind_high":
            sensor_data["Viento"]["vel"] = 50 + random.randint(0, 20)
            alerts.append(("🌪️ VIENTOS FUERTES", "#7209b7"))
            new_alert_added = True

    for key in history:
        if len(history[key]) > 20:
            history[key].pop(0)
    
    history["temp"].append(sensor_data["DHT22"]["temp"])
    history["hum"].append(sensor_data["DHT22"]["hum"])
    history["pres"].append(sensor_data["BME280"]["pres"])
    history["lux"].append(sensor_data["BH1750"]["lux"])
    history["vel"].append(sensor_data["Viento"]["vel"])
    return new_alert_added

def data_card(title, emoji, value, unit, color1, color2, is_alert=False):
    return ft.Container(
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Text(emoji, size=34),
                ft.Text(title, color="white70", size=14),
                ft.Text(f"{value} {unit}", weight=ft.FontWeight.BOLD, size=26, color="white"),
            ],
        ),
        width=170,
        height=170,
        border_radius=35,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[color1, color2],
        ),
        shadow=ft.BoxShadow(
            spread_radius=6,
            blur_radius=30,
            color="#38000000",
            offset=ft.Offset(0, 8),
        ),
        animate=ft.Animation(500, "bounceOut") if is_alert else None,
        border=ft.border.all(3, "#ff0000") if is_alert else None
    )

def create_chart(data, line_color, title):
    if not data:
        # Si no hay datos, muestra un gráfico con un punto ficticio para definir el rango.
        data_points_for_chart = [ft.LineChartDataPoint(0, 0)] 
        min_y_val = -1 
        max_y_val = 1
    else:
        data_points_for_chart = [ft.LineChartDataPoint(i, val) for i, val in enumerate(data)]
        min_val = min(data)
        max_val = max(data)

        if len(data) == 1: # Solo un punto de dato
            min_y_val = min_val - 0.5
            max_y_val = max_val + 0.5
        elif min_val == max_val: # Múltiples puntos, todos con el mismo valor
            min_y_val = min_val - 0.5
            max_y_val = max_val + 0.5
        else: # Múltiples puntos con diferentes valores
            padding = (max_val - min_val) * 0.1
            # Asegurar un padding mínimo si los valores son muy cercanos pero no iguales
            if padding == 0 and (max_val - min_val) > 0: 
                padding = 0.1 # Un padding muy pequeño pero existente
            elif padding == 0: # Si min_val y max_val son realmente iguales (cubierto arriba, pero por si acaso)
                padding = 0.5

            min_y_val = min_val - padding
            max_y_val = max_val + padding
        
        # Asegurar que min_y sea estrictamente menor que max_y
        if min_y_val >= max_y_val:
            max_y_val = min_y_val + 1 # Asegurar un rango visible mínimo de 1 unidad


    chart = ft.LineChart(
        data_series=[
            ft.LineChartData(
                data_points=data_points_for_chart,
                color=line_color,
                stroke_width=3,
                curved=True, # Hace las líneas curvas
                # Podrías experimentar con 'point_szie' si quieres ver los puntos individuales
                # point_size=5 
            )
        ],
        border=ft.border.all(1, "#37474f"),
        left_axis=ft.ChartAxis(labels_size=40, show_labels=True), # Asegurar que las etiquetas se muestren
        bottom_axis=ft.ChartAxis(labels_size=0, show_labels=False), # No mostrar etiquetas en el eje X
        tooltip_bgcolor="#CC121212", 
        min_y=min_y_val,
        max_y=max_y_val,
        expand=True,
        height=150
    )
    
    return ft.Column(
        controls=[
            ft.Text(title, color="white70", size=12),
            chart
        ],
        spacing=5
    )

def main(page: ft.Page):
    page.title = "SCADA Estación Meteorológica"
    page.theme_mode = ft.ThemeMode.DARK 
    page.bgcolor = "#0f172a"
    page.padding = 30
    page.scroll = ft.ScrollMode.AUTO

    temp_card = ft.Column()
    hum_card = ft.Column()
    pres_card = ft.Column()
    luz_card = ft.Column()
    lluvia_card = ft.Column()
    viento_card = ft.Column()
    alert_container = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO, height=150)
    charts_container = ft.Column(spacing=20)
    reloj = ft.Text(f"⏱️ {datetime.now().strftime('%H:%M:%S')}", color="#DDDDDD", size=14)

    def play_alert_sound_effect():
        sound_indicator = ft.Container(
            width=0, height=0, content=ft.Text("🔔", size=1),
            animate_opacity=ft.Animation(1000, "easeOut"), opacity=0
        )
        return sound_indicator

    # Lista para mantener referencias a los indicadores de sonido activos si se necesitan manejar
    # active_sound_indicators = []

    def update_ui(e=None):
        new_alert_generated = simulate_sensor_reading()

        temp = sensor_data["DHT22"]["temp"]
        hum = sensor_data["DHT22"]["hum"]
        pres = sensor_data["BME280"]["pres"]
        lux = sensor_data["BH1750"]["lux"]
        rain = sensor_data["YL-83"]["rain"]
        vel = sensor_data["Viento"]["vel"]
        dir_viento = sensor_data["Viento"]["dir"]

        temp_alert = temp > 35 or temp < 0
        hum_alert = hum > 80 or hum < 20
        wind_alert = vel > 30
        rain_alert = rain

        temp_card.controls = [data_card("Temp DHT22", "🌡️", temp, "°C", "#FFB347", "#FF7043", temp_alert)]
        hum_card.controls = [data_card("Humedad", "💧", hum, "%", "#76c7f2", "#2980b9", hum_alert)]
        pres_card.controls = [data_card("Presión", "🌬️", pres, "hPa", "#90a4ae", "#607d8b")]
        luz_card.controls = [data_card("Luz", "💡", lux, "lux", "#ffe57f", "#fdd835")]
        lluvia_card.controls = [data_card("Lluvia", "🌧️" if rain else "☀️", "Sí" if rain else "No", "", "#4fc3f7", "#0288d1", rain_alert)]
        viento_card.controls = [data_card("Viento", "🍃", vel, f"km/h {dir_viento}", "#a8edea", "#fed6e3", wind_alert)]

        alert_controls = []
        for text, alert_color_hex in alerts[-3:]: 
            bg_color_with_opacity = f"#33{alert_color_hex.lstrip('#')}"
            alert_controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(name="warning_amber_rounded", color=alert_color_hex), 
                            ft.Text(text, color="white", weight=ft.FontWeight.BOLD)
                        ],
                        spacing=10
                    ),
                    bgcolor=bg_color_with_opacity,
                    padding=10,
                    border_radius=10,
                    animate_opacity=ft.Animation(500, "easeOut"),
                )
            )
        alert_container.controls = alert_controls

        charts_container.controls = [
            create_chart(history["temp"], "#FF7043", "Temperatura (°C)"),
            create_chart(history["hum"], "#2980b9", "Humedad (%)"),
            create_chart(history["vel"], "#a8edea", "Velocidad Viento (km/h)"),
        ]
        
        reloj.value = f"⏱️ {datetime.now().strftime('%H:%M:%S')}"
        
        if new_alert_generated:
            sound_indicator_control = play_alert_sound_effect()
            page.add(sound_indicator_control)
            # active_sound_indicators.append(sound_indicator_control)

            def animate_sound_indicator(indicator):
                indicator.opacity = 1 
                if page.controls: # Asegurarse que la página aún tiene controles (no está cerrándose)
                    page.update()
                time.sleep(0.05) 
                indicator.opacity = 0 
                if page.controls:
                    page.update()
                # No se remueve el control aquí para simplificar y evitar problemas de concurrencia.
                # El control es 0x0 y opacity 0, así que no debería molestar.
            
            threading.Thread(target=animate_sound_indicator, args=(sound_indicator_control,)).start()

        if page.controls: # Solo actualizar si la página aún tiene controles (no se está cerrando)
             page.update()

    page.add(
        ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=25,
            controls=[
                ft.Text("🛰️ SCADA - Estación Meteorológica", size=28, weight=ft.FontWeight.BOLD, color="white"),
                reloj,
                ft.Text("⚠️ ALERTAS", size=16, color="white70"),
                alert_container,
                ft.Row([temp_card, hum_card, pres_card], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                ft.Row([luz_card, lluvia_card, viento_card], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                ft.Text("📊 HISTORIAL", size=16, color="white70"),
                charts_container,
            ]
        )
    )

    def auto_update_loop():
        while True:
            time.sleep(2) 
            # CORRECCIÓN: Eliminada la comprobación 'page.window_destroyed'
            try:
                # Verificar si la página y sus controles aún existen antes de actualizar.
                # Esto es una medida de precaución simple.
                if page and page.controls:
                    update_ui() 
            except Exception as e:
                print(f"Error en auto_update_loop: {e}")
                # Si ocurre un error muy frecuentemente aquí, podría ser necesario detener el bucle.
                # Por ahora, solo lo imprimimos.
                pass # Continuar el bucle


    import threading
    update_thread = threading.Thread(target=auto_update_loop, daemon=True)
    update_thread.start()

    update_ui()

ft.app(target=main)