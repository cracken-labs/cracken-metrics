from typing import Optional
from sqlmodel import Field, SQLModel

class WidgetBase(SQLModel):
    title: str = Field(index=True, description="Название виджета/метрики для отображения в Grafana")
    formula: str = Field(description="Математическая формула стратегии, например: SBER / GAZP")
    color: str = Field(default="#3274d9", description="Hex-код цвета линии графика, например: #3274d9")
    
    # Координаты сетки Grafana (Ширина экрана Grafana по умолчанию = 24 колонки)
    grid_x: int = Field(default=0, description="Позиция по оси X (0-23)")
    grid_y: int = Field(default=0, description="Позиция по оси Y")
    grid_w: int = Field(default=12, description="Ширина виджета в колонках сетки (1-24)")
    grid_h: int = Field(default=8, description="Высота виджета")

class Widget(WidgetBase, table=True):
    """Таблица в SQLite для хранения состояния Control Plane"""
    id: Optional[int] = Field(default=None, primary_key=True)

class WidgetCreate(WidgetBase):
    """Схема для валидации входящих данных при создании нового виджета"""
    pass

class WidgetUpdate(SQLModel):
    """Схема для частичного обновления виджета (например, только поменять цвет или подвинуть)"""
    title: Optional[str] = None
    formula: Optional[str] = None
    color: Optional[str] = None
    grid_x: Optional[int] = None
    grid_y: Optional[int] = None
    grid_w: Optional[int] = None
    grid_h: Optional[int] = None
