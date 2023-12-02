import streamlit as st

from Converted_EXPRESS_ГЛАВА_2_1_Метрики_и_графики_ЗАДАНИЯ import (
    Active_peoples,
    Dynamics_of_users_and_couriers_share,
    Indicator_dynamics_orders,
    New_peoples,
    New_Peoples_Change,
    New_Peoples_Share,
    Order_related_indicators,
    Peoples_share,
    Total_peoples,
    Total_peoples_growth,
    average_delivery_time,
    orders_users_per_courier,
)

st.set_page_config(layout="wide")
st.header('Что происходит? (Общая ситуация по заказам) (Задания)')
st.title('Это - Глава 2 - Урок 1 - Метрики, задания')

chart = iter([Total_peoples,
              New_peoples,
              New_Peoples_Change,
              Total_peoples_growth,
              Active_peoples,
              Peoples_share,
              New_Peoples_Share,
              Order_related_indicators,
              Dynamics_of_users_and_couriers_share,
              orders_users_per_courier,
              average_delivery_time,
              Indicator_dynamics_orders])

num_rows = 6
num_cols = 2

for _ in range(num_rows):
    cols = st.columns(num_cols)
    for j in range(num_cols):
        cols[j].plotly_chart(next(chart), use_container_width=True)
