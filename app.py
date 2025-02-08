from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import os
import json

app = Flask(__name__)

# Загружаем данные
df = pd.read_csv("vacancies_january_2.csv")

# Добавьте столбцы с широтой и долготой для каждого города (это нужно сделать заранее)
city_coordinates = {
    'Алматы': {'lat': 43.222, 'lon': 76.8512},
    'Нур-Султан': {'lat': 51.169, 'lon': 71.4491},
    'Шымкент': {'lat': 42.341, 'lon': 69.5901},
    'Караганда': {'lat': 49.802, 'lon': 73.092},
    'Атырау': {'lat': 47.138, 'lon': 51.926},
    # Добавьте остальные города с их координатами
}

# Создаем папку для графиков, если её нет
if not os.path.exists("static"):
    os.makedirs("static")

@app.route("/")
def index():
    city = request.args.get("city")  
    filtered_df = df.copy()

    # Получаем список уникальных городов
    cities = sorted(df["city"].dropna().unique())

    if city:
        filtered_df = filtered_df[filtered_df["city"] == city]

    # Создание графиков для профессий и зарплат (как у вас в коде)
    if not filtered_df.empty:  
        top_jobs = filtered_df['name'].value_counts().nlargest(10)
        fig1 = px.bar(x=top_jobs.index, y=top_jobs.values, title="Топ-10 профессий", labels={'x': 'Профессия', 'y': 'Количество'})
        fig1.write_html("static/chart1.html")  

    if "salary_from" in filtered_df.columns and not filtered_df["salary_from"].isna().all():
        filtered_df["salary_from"] = pd.to_numeric(filtered_df["salary_from"], errors="coerce")
        filtered_df = filtered_df.dropna(subset=["salary_from"])  
        if not filtered_df.empty:  
            fig2 = px.histogram(filtered_df, x="salary_from", title="Распределение зарплат", labels={'salary_from': 'Зарплата'})
            fig2.write_html("static/chart2.html")

    # Карта с количеством вакансий по городам
    city_counts = filtered_df["city"].value_counts()

    # Создаем данные для карты
    map_data = []
    for city, count in city_counts.items():
        if city in city_coordinates:
            map_data.append({
                'city': city,
                'vacancies_count': count,
                'latitude': city_coordinates[city]['lat'],
                'longitude': city_coordinates[city]['lon']
            })

    # Создаем график карты с ограничением на Казахстан
    map_df = pd.DataFrame(map_data)
    fig_map = px.scatter_geo(map_df,
                             lat='latitude',
                             lon='longitude',
                             hover_name='city',
                             size='vacancies_count',
                             color='vacancies_count',
                             title="Вакансии по городам Казахстана",
                             hover_data={'city': True, 'vacancies_count': True},
                             projection="mercator",  # Используем стандартную проекцию
                             scope="asia",  # Ограничиваем карту только Азией
                             center={"lat": 48.0196, "lon": 66.9237},  # Центр Казахстана
                             template="plotly_dark")  # Темный стиль для карты
    fig_map.write_html("static/map.html")

    return render_template("index.html", city=city, cities=cities)

if __name__ == "__main__":
    app.run(debug=True)
