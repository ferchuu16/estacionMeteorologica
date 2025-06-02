import flet as ft
import random
import asyncio
from collections import deque
from datetime import datetime, timedelta
import math

class WeatherSensor:
    """Clase base para sensores meteorológicos"""
    def __init__(self, name, unit, min_val, max_val, normal_range, icon):
        self.name = name
        self.unit = unit
        self.min_val = min_val
        self.max_val = max_val
        self.normal_range = normal_range  # (min_normal, max_normal)
        self.icon = icon
        self.history = deque(maxlen=30)  # Últimos 30 valores
        self.timestamps = deque(maxlen=30)
        self.current_value = 0
        self.is_alert = False
    
    def simulate_value(self):
        """Simula un valor del sensor con variación realista"""
        # Generar valor base con tendencia suave
        base_value = (self.min_val + self.max_val) / 2
        variation = (self.max_val - self.min_val) * 0.3
        noise = random.uniform(-variation, variation)
        
        # Añadir algo de persistencia al valor anterior
        if self.history:
            self.current_value = self.history[-1] * 0.7 + (base_value + noise) * 0.3
        else:
            self.current_value = base_value + noise
        
        # Limitar al rango válido
        self.current_value = max(self.min_val, min(self.max_val, self.current_value))
        
        # Almacenar en historial
        self.history.append(self.current_value)
        self.timestamps.append(datetime.now())
        
        # Verificar condición de alerta
        self.is_alert = (self.current_value < self.normal_range[0] or 
                        self.current_value > self.normal_range[1])
        
        return self.current_value

class AnimatedCard(ft.Control):
    """Tarjeta de sensor con animaciones y gráfico integrado"""
    def __init__(self, sensor):
        super().__init__()
        self.sensor = sensor
        self.card_container = None
        self.value_text = None
        self.alert_icon = None
        self.trend_container = None
        self.update_indicator = None
        
    def build(self):
        # Indicador de actualización
        self.update_indicator = ft.Container(
            width=8,
            height=8,
            border_radius=4,
            bgcolor=ft.Colors.GREEN,
            opacity=0,
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
        )
        
        # Texto del valor principal
        self.value_text = ft.Text(
            f"{self.sensor.current_value:.1f}",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        )
        
        # Icono de alerta
        self.alert_icon = ft.Icon(
            ft.Icons.WARNING_ROUNDED,
            color=ft.Colors.YELLOW,
            size=20,
            opacity=0,
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_OUT)
        )
        
        # Gráfico de tendencia (simulado con caracteres)
        self.trend_container = ft.Container(
            content=self._create_mini_chart(),
            height=60,
            padding=ft.padding.all(5)
        )
        
        # Contenedor principal de la tarjeta
        self.card_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(self.sensor.icon, color=ft.Colors.WHITE70, size=24),
                   
                    self.update_indicator,
                    self.alert_icon
                ]),
                ft.Text(
                    self.sensor.name,
                    size=14,
                    color=ft.Colors.WHITE70,
                    weight=ft.FontWeight.W_500
                ),
                ft.Row([
                    self.value_text,
                    ft.Text(
                        self.sensor.unit,
                        size=16,
                        color=ft.Colors.WHITE70,
                        weight=ft.FontWeight.W_400
                    )
                ], alignment=ft.MainAxisAlignment.CENTER),
                self.trend_container
            ], spacing=8),
            width=200,
            height=180,
            padding=ft.padding.all(16),
            border_radius=12,
            gradient=self._get_gradient(),
            animate=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
            animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            animate_offset=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        )
        
        return self.card_container
    
    def _get_gradient(self):
        """Obtiene el gradiente basado en el estado del sensor"""
        if self.sensor.is_alert:
            if self.sensor.current_value > self.sensor.normal_range[1]:
                # Alerta alta (calor, humedad alta, viento fuerte)
                return ft.LinearGradient(
                    colors=[ft.Colors.RED_700, ft.Colors.RED_900],
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right
                )
            else:
                # Alerta baja (frío, humedad baja)
                return ft.LinearGradient(
                    colors=[ft.Colors.BLUE_700, ft.Colors.BLUE_900],
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right
                )
        else:
            # Estado normal
            return ft.LinearGradient(
                colors=[ft.Colors.BLUE_GREY_800, ft.Colors.BLUE_GREY_900],
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right
            )
    
    def _create_mini_chart(self):
        """Crea un mini gráfico de barras ASCII"""
        if len(self.sensor.history) < 2:
            return ft.Text("Sin datos", size=10, color=ft.Colors.WHITE54)
        
        # Normalizar valores para el gráfico
        min_val = min(self.sensor.history)
        max_val = max(self.sensor.history)
        
        if max_val == min_val:
            bars = "▂" * len(self.sensor.history)
        else:
            normalized = [(val - min_val) / (max_val - min_val) for val in self.sensor.history]
            bar_chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
            bars = "".join([bar_chars[int(val * 7)] for val in normalized])
        
        return ft.Column([
            ft.Text("Tendencia", size=10, color=ft.Colors.WHITE54),
            ft.Text(bars, size=12, color=ft.Colors.WHITE70, font_family="monospace")
        ])
    
    async def update_data(self):
        """Actualiza los datos del sensor con animaciones"""
        # Mostrar indicador de actualización
        self.update_indicator.opacity = 1
        await self.update_async()
        
        # Simular nuevo valor
        old_value = self.sensor.current_value
        new_value = self.sensor.simulate_value()
        
        # Animación de salida del valor anterior
        self.value_text.opacity = 0.3
        self.value_text.scale = 0.8
        await self.update_async()
        await asyncio.sleep(0.15)
        
        # Actualizar valor y animación de entrada
        self.value_text.value = f"{new_value:.1f}"
        self.value_text.opacity = 1
        self.value_text.scale = 1.1
        await self.update_async()
        await asyncio.sleep(0.15)
        
        # Normalizar escala
        self.value_text.scale = 1
        await self.update_async()
        
        # Actualizar gradiente y alerta
        self.card_container.gradient = self._get_gradient()
        self.alert_icon.opacity = 1 if self.sensor.is_alert else 0
        
        # Actualizar gráfico de tendencia
        self.trend_container.content = self._create_mini_chart()
        
        # Animación sutil de la tarjeta si hay cambio significativo
        if abs(new_value - old_value) > (self.sensor.max_val - self.sensor.min_val) * 0.05:
            self.card_container.offset = ft.transform.Offset(0, -0.02)
            await self.update_async()
            await asyncio.sleep(0.1)
            self.card_container.offset = ft.transform.Offset(0, 0)
        
        # Ocultar indicador de actualización
        await asyncio.sleep(0.3)
        self.update_indicator.opacity = 0
        await self.update_async()

class WeatherDashboard:
    """Dashboard principal de la estación meteorológica"""
    def __init__(self, page: ft.Page):
        self.page = page
        self.sensors = self._initialize_sensors()
        self.cards = []
        self.is_updating = False
        self.last_update_time = None
        
    def _initialize_sensors(self):
        """Inicializa los sensores con sus parámetros"""
        return [
            WeatherSensor("Temperatura", "°C", 10, 35, (15, 28), ft.Icons.THERMOSTAT),
            WeatherSensor("Humedad", "%", 20, 90, (30, 70), ft.Icons.WATER_DROP),
            WeatherSensor("Presión", "hPa", 980, 1030, (1000, 1020), ft.Icons.SPEED),
            WeatherSensor("Luminosidad", "lux", 0, 1000, (100, 800), ft.Icons.LIGHT_MODE),
            WeatherSensor("Viento", "km/h", 0, 40, (0, 20), ft.Icons.AIR),
            WeatherSensor("Lluvia", "mm", 0, 100, (0, 5), ft.Icons.WATER)
        ]
    
    def build_dashboard(self):
        """Construye la interfaz del dashboard"""
        # Crear tarjetas animadas
        self.cards = [AnimatedCard(sensor) for sensor in self.sensors]
        
        # Indicador de estado global
        status_indicator = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.SENSORS, color=ft.Colors.GREEN, size=16),
                ft.Text("Sistema Activo", color=ft.Colors.GREEN, size=12, weight=ft.FontWeight.W_500),
                ft.Container(
                    width=8,
                    height=8,
                    border_radius=4,
                    bgcolor=ft.Colors.GREEN,
                    animate_opacity=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
                )
            ], spacing=8),
            padding=ft.padding.all(12),
            border_radius=8,
            bgcolor=ft.Colors.GREEN_50,
            border=ft.border.all(1, ft.Colors.GREEN_200)
        )
        
        # Botón de actualización con animación
        update_button = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.REFRESH, size=20),
                ft.Text("Actualizar Datos", size=14, weight=ft.FontWeight.W_500)
            ], spacing=8, tight=True),
            on_click=self._on_update_click,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                shape=ft.RoundedRectangleBorder(radius=8)
            )
        )
        
        # Layout principal
        return ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text("🏭 Estación Meteorológica Industrial", 
                           size=28, weight=ft.FontWeight.BOLD, 
                           color=ft.Colors.BLUE_GREY_800),
                    ft.Text("Monitoreo en Tiempo Real - El Calafate, Santa Cruz", 
                           size=14, color=ft.Colors.BLUE_GREY_600),
                ], spacing=4),
                padding=ft.padding.only(bottom=20)
            ),
            
            ft.Row([status_indicator, update_button], 
                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Container(height=20),  # Espaciado
            
            ft.ResponsiveRow([
                ft.Column([card], col={"sm": 6, "md": 4, "lg": 2}) 
                for card in self.cards
            ], spacing=16),
            
            ft.Container(
                content=ft.Text(
                    f"Última actualización: {datetime.now().strftime('%H:%M:%S')}",
                    size=12, color=ft.Colors.BLUE_GREY_400
                ),
                padding=ft.padding.only(top=20),
                alignment=ft.alignment.center
            )
        ], spacing=16, scroll=ft.ScrollMode.AUTO)
    
    async def _on_update_click(self, e):
        """Maneja el clic del botón de actualización"""
        if self.is_updating:
            return
            
        self.is_updating = True
        
        # Animar todas las tarjetas
        tasks = [card.update_data() for card in self.cards]
        await asyncio.gather(*tasks)
        
        self.is_updating = False
        self.last_update_time = datetime.now()
    
    async def auto_update_loop(self):
        """Loop de actualización automática cada 5 segundos"""
        while True:
            await asyncio.sleep(5)
            if not self.is_updating:
                await self._on_update_click(None)

async def main(page: ft.Page):
    # Configuración de la página
    page.title = "Dashboard Meteorológico Industrial"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.GREY_50
    page.padding = 20
    page.window_width = 1200
    page.window_height = 800
    page.window_resizable = True
    
    # Crear dashboard
    dashboard = WeatherDashboard(page)
    page.add(dashboard.build_dashboard())
    
    # Inicializar valores
    for card in dashboard.cards:
        card.sensor.simulate_value()
        await card.update_data()
    
    # Iniciar loop de actualización automática
    asyncio.create_task(dashboard.auto_update_loop())

if __name__ == "__main__":
    ft.app(target=main)