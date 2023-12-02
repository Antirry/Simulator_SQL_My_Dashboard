#!/usr/bin/env python
# coding: utf-8

#     !pip install ipykernel
#     !pip install pandas
#     !pip install plotly
#     !pip install psycopg2
#     !pip install --upgrade nbformat

# In[31]:


from configparser import ConfigParser

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from psycopg2 import connect

# In[32]:


def format_cursor(cursor):
    return [cursor.fetchall(),
             (desc[0] for desc in cursor.description)]


# In[33]:


def data(data_in_query):
    return pd.DataFrame(data_in_query[0],
                        columns=data_in_query[1])


# In[34]:


config = ConfigParser()
config.read('TEST.ini', encoding="utf-8")

config = {i: config['postgresql'][i]
           for i in config['postgresql']}


# ## СРАВНЕНИЕ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ

# In[35]:


with connect(**config) as connect_1:
    with connect_1.cursor() as cursor_1:
        cursor_1.execute("""
SELECT date::DATE,
total_users,
new_users,
total_couriers,
new_couriers
FROM (
    SELECT COUNT(DISTINCT user_id) new_users,
    (SUM(COUNT(DISTINCT user_id)) OVER (ORDER BY date))::INTEGER total_users,
    date
    FROM (
        SELECT DISTINCT user_id,
        date_trunc('day', MIN(time) OVER (PARTITION BY user_id ORDER BY order_id)) AS date
        FROM user_actions) t1
    GROUP BY date
    ORDER BY date
) users
JOIN (
    SELECT COUNT(DISTINCT courier_id) new_couriers,
    (SUM(COUNT(DISTINCT courier_id)) OVER (ORDER BY date))::INTEGER total_couriers,
    date
    FROM (
        SELECT DISTINCT courier_id,
            date_trunc('day', MIN(time) OVER (PARTITION BY courier_id ORDER BY courier_id)) AS date
            FROM courier_actions
        ) t1
    GROUP BY date
    ORDER BY date
) couriers
USING(date)
        """)
        df_cursor_number_persons = data(format_cursor(cursor_1))

# print(df_cursor_number_persons.dtypes, sep="\n \n")


# In[36]:


fig = px.line(df_cursor_number_persons,
             x='date',
             y='total_users',
             title='Сравнение всех пользователей',
             template='plotly_dark'
)

fig.update_traces(
    line_color=px.colors.qualitative.Set3[3],
    showlegend=True,
    name='total_users'
)

fig1 = px.line(
    df_cursor_number_persons,
    x='date',
    y='total_couriers'
)

fig1.update_traces(
    line_color=px.colors.qualitative.Set3[5],
    showlegend=True,
    name='total_couriers'
)

fig.add_trace(fig1.data[0])

fig.update_layout(barmode='group',
                  showlegend=True,
                  legend_title='Total_peoples'
)

fig.update_yaxes(title_text='')
fig.update_xaxes(title_text='')

Total_peoples = fig


# ## СРАВНЕНИЕ НОВЫХ ПОЛЬЗОВАТЕЛЕЙ

# In[37]:


fig = px.line(df_cursor_number_persons,
             x='date',
             y='new_users',
             title='Сравнение новых пользователей',
             template='plotly_dark'
)

fig.update_traces(
    line_color=px.colors.qualitative.Set3[3],
    showlegend=True,
    name='new_users'
)

fig1 = px.line(
    df_cursor_number_persons,
    x='date',
    y='new_couriers'
)

fig1.update_traces(
    line_color=px.colors.qualitative.Set3[5],
    showlegend=True,
    name='new_couriers'
)

fig.add_trace(fig1.data[0])

fig.update_layout(barmode='group',
                  showlegend=True,
                  legend_title='New_peoples'
)

fig.update_yaxes(title_text='')
fig.update_xaxes(title_text='')

New_peoples = fig


# ## ПРИРОСТ ЧИСЛА ЛЮДЕЙ НА ПЛОЩАДКЕ

# In[38]:


with connect(**config) as connect_1:
    with connect_1.cursor() as cursor_1:
        cursor_1.execute("""
SELECT date::DATE AS date,
new_users,
new_couriers,
total_couriers,
total_users,
ROUND((new_users::DECIMAL / LAG(new_users, 1) OVER (ORDER BY date) - 1) * 100, 2)::FLOAT new_users_change,
ROUND((new_couriers::DECIMAL / LAG(new_couriers, 1) OVER (ORDER BY date) - 1) * 100, 2)::FLOAT new_couriers_change,
ROUND((total_users::DECIMAL / LAG(total_users, 1) OVER (ORDER BY date) - 1) * 100, 2)::FLOAT total_users_growth,
ROUND((total_couriers::DECIMAL / LAG(total_couriers, 1) OVER (ORDER BY date) - 1) * 100, 2)::FLOAT total_couriers_growth
FROM (
    SELECT COUNT(DISTINCT user_id) new_users,
    (SUM(COUNT(DISTINCT user_id)) OVER (ORDER BY date))::INTEGER total_users,
    date
    FROM (
        SELECT DISTINCT user_id,
        date_trunc('day', MIN(time) OVER (PARTITION BY user_id ORDER BY order_id)) AS date
        FROM user_actions) t1
    GROUP BY date
    ORDER BY date
) users
JOIN (
    SELECT COUNT(DISTINCT courier_id) new_couriers,
    (SUM(COUNT(DISTINCT courier_id)) OVER (ORDER BY date))::INTEGER total_couriers,
    date
    FROM (
        SELECT DISTINCT courier_id,
            date_trunc('day', MIN(time) OVER (PARTITION BY courier_id ORDER BY courier_id)) AS date
            FROM courier_actions
        ) t1
    GROUP BY date
    ORDER BY date
) couriers
USING(date)
ORDER BY date""")
        df_cursor_Relative_dynamics_people = data(
            format_cursor(cursor_1))


# df_cursor_Relative_dynamics_people['date'] = df_cursor_Relative_dynamics_people['date'].dt.date

# print(df_cursor_Relative_dynamics_people.dtypes, sep="\n \n")


# In[39]:


df_filtered = df_cursor_Relative_dynamics_people.dropna(
    subset=['total_users_growth',
            'total_couriers_growth',
            'new_users_change',
            'new_couriers_change']
)

fig = px.bar(df_filtered,
             x='date',
             y='new_users_change',
             title='Прирост числа пользователей / Курьеров',
             template='plotly_dark'
)

fig.update_traces(
    marker_color=px.colors.qualitative.Set3[3],
    showlegend=True,
    name='new_users_change'
)

fig1 = px.bar(
    df_filtered,
    x='date',
    y='new_couriers_change'
)

fig1.update_traces(
    marker_color=px.colors.qualitative.Set3[5],
    showlegend=True,
    name='new_couriers_change'
)

fig.add_trace(fig1.data[0])

fig.update_layout(barmode='group',
                  showlegend=True,
                  legend_title='New_Peoples_Change'
)

fig.update_yaxes(title_text='')
fig.update_xaxes(title_text='')

New_Peoples_Change = fig


# In[40]:


fig = px.bar(df_filtered,
             x='date',
             y='total_users_growth',
             title='Прирост общего числа пользователей, курьеров',
             template='plotly_dark'
)

fig.update_traces(marker_color=px.colors.qualitative.Set3[3],
                  showlegend=True,
                  name='total_users_growth'
)

fig1 = px.bar(df_filtered,
              x='date',
              y='total_couriers_growth'
)

fig1.update_traces(
    marker_color=px.colors.qualitative.Set3[5],
    showlegend=True,
    name='total_couriers_growth'
)

fig.add_trace(fig1.data[0])

fig.update_layout(
    barmode='group',
    showlegend=True,
    legend_title='Total_peoples_growth'
)

fig.update_yaxes(title_text='')
fig.update_xaxes(title_text='')

Total_peoples_growth = fig


# ## Динамика платящих пользователей и активных курьеров:

# In[41]:


with connect(**config) as connect_1:
    with connect_1.cursor() as cursor_1:
        cursor_1.execute("""
SELECT date,
       paying_users,
       active_couriers,
       round(100 * paying_users::decimal / total_users, 2) as paying_users_share,
       round(100 * active_couriers::decimal / total_couriers, 2) as active_couriers_share
FROM
(
    SELECT start_date as date,
        new_users,
        new_couriers,
        (sum(new_users) OVER (ORDER BY start_date))::int as total_users,
        (sum(new_couriers) OVER (ORDER BY start_date))::int as total_couriers
    FROM
    (
        SELECT start_date,
               count(courier_id) as new_couriers
        FROM
        (
            SELECT courier_id,
                min(time::date) as start_date
            FROM courier_actions
            GROUP BY courier_id
        ) t1
        GROUP BY start_date
    ) t2
    LEFT JOIN
    (
        SELECT start_date,
            count(user_id) as new_users
        FROM
        (
            SELECT user_id,
            min(time::date) as start_date
            FROM user_actions
            GROUP BY user_id
        ) t3
    GROUP BY start_date
    ) t4
    using (start_date)
) t5
LEFT JOIN
(
    SELECT time::date as date,
        count(distinct courier_id) as active_couriers
    FROM courier_actions
    WHERE order_id not in
    (
        SELECT order_id
        FROM user_actions
        WHERE action = 'cancel_order'
    )
    GROUP BY date
) t6
using (date)
LEFT JOIN
(
    SELECT time::date as date,
        count(distinct user_id) as paying_users
    FROM user_actions
    WHERE order_id not in
    (
        SELECT order_id
        FROM user_actions
        WHERE action = 'cancel_order'
    )
    GROUP BY date
) t7
using (date)
        """)
        df_share_peoples = pd.DataFrame(data(format_cursor(cursor_1)))

# print(df_share_peoples.dtypes)


# In[42]:


fig = px.line(df_share_peoples,
             x='date',
             y='paying_users',
             title='Динамика платящих пользователей / активных курьеров',
             template='plotly_dark'
)

fig.update_traces(
    line_color=px.colors.qualitative.Set3[3],
    showlegend=True,
    name='paying_users'
)

fig1 = px.line(
    df_share_peoples,
    x='date',
    y='active_couriers'
)

fig1.update_traces(
    line_color=px.colors.qualitative.Set3[5],
    showlegend=True,
    name='active_couriers'
)

fig.add_trace(fig1.data[0])

fig.update_layout(barmode='group',
                  showlegend=True,
                  legend_title='Active_peoples'
)

fig.update_yaxes(title_text='')
fig.update_xaxes(title_text='')

Active_peoples = fig


# In[43]:


fig = px.line(df_share_peoples,
             x='date',
             y='paying_users_share',
             title='Динамика платящей доли пользователей / активной доли курьеров',
             template='plotly_dark'
)

fig.update_traces(
    line_color=px.colors.qualitative.Set3[3],
    showlegend=True,
    name='paying_users_share'
)

fig1 = px.line(
    df_share_peoples,
    x='date',
    y='active_couriers_share'
)

fig1.update_traces(
    line_color=px.colors.qualitative.Set3[5],
    showlegend=True,
    name='active_couriers_share'
)

fig.add_trace(fig1.data[0])

fig.update_layout(barmode='group',
                  showlegend=True,
                  legend_title='Peoples_share'
)

fig.update_yaxes(rangemode='tozero', title_text='')
fig.update_xaxes(title_text='')

Peoples_share = fig


# ## Доли пользователей с одним и несколькими заказами:

# In[44]:


with connect(**config) as connect_1:
    with connect_1.cursor() as cursor_1:
        cursor_1.execute("""
SELECT date::date date,
       round((users_1_order_per_day::decimal / paying_users) * 100,
             2)::float single_order_users_share,
       round(100 - (users_1_order_per_day::decimal / paying_users) * 100,
             2)::float several_orders_users_share
FROM
(
    SELECT count(distinct user_id)
        filter (WHERE order_id not in
                    (SELECT order_id
                        FROM   user_actions
                        WHERE  "action" like 'can%')
                ) paying_users,
        date_trunc('day', time) date
    FROM user_actions
    GROUP BY date
    ORDER BY date
) paying_users
JOIN
(
    SELECT
        count(user_id) users_1_order_per_day,
        date_trunc('day', time) date
    FROM
    (
        SELECT user_id,
            time,
            count(order_id) OVER
            (PARTITION BY user_id,
            date_trunc('day', time)) count_orders
        FROM   user_actions
        WHERE  order_id not in (SELECT order_id
                                FROM   user_actions
                                WHERE  "action" like 'can%')
        ORDER BY 1, time
    ) t1
    WHERE count_orders = 1
    GROUP BY date
    ORDER BY date
) users_count_1_of_orders_per_day
using(date)
        """)
        df_share_users = data(format_cursor(cursor_1))

# print(df_share_users.dtypes)


# In[45]:


fig = px.bar(df_share_users,
             x='date',
             y='single_order_users_share',
             title='Доли пользователей с одним / несколькими заказами (%)',
             template='plotly_dark'
)

fig.update_traces(
    marker_color=px.colors.qualitative.Set3[3],
    showlegend=True,
    name='single_order_users_share'
)

fig1 = px.bar(
    df_share_users,
    x='date',
    y='several_orders_users_share'
)

fig1.update_traces(
    marker_color=px.colors.qualitative.Set3[5],
    showlegend=True,
    name='several_orders_users_share'
)

fig.add_trace(fig1.data[0])

fig.update_layout(barmode='relative',
                  showlegend=True,
                  legend_title='New_Peoples_Share'
)

fig.update_yaxes(title_text='')
fig.update_xaxes(title_text='')

New_Peoples_Share = fig


# In[46]:


with connect(**config) as connect_1:
    with connect_1.cursor() as cursor_1:
        cursor_1.execute("""
SELECT date::date,
       orders,
       first_orders,
       new_users_orders,
       round((first_orders::decimal / orders) * 100, 2) first_orders_share,
       round((new_users_orders::decimal / orders) * 100, 2) new_users_orders_share
FROM
(
    SELECT
        count(user_id) orders,
        date_trunc('day', time) date
    FROM user_actions
    WHERE order_id not in (
        SELECT order_id
        FROM   user_actions
        WHERE  "action" like 'can%')
    GROUP BY date
    ORDER BY date) all_create_orders_users
JOIN
(
    SELECT
        date,
        count(user_id) first_orders
    FROM
    (
        SELECT user_id,
                min(date_trunc('day', time)) date
            FROM   user_actions
            WHERE  order_id not in (SELECT order_id
                                    FROM   user_actions
                                    WHERE  "action" like 'can%')
            GROUP BY user_id
            ORDER BY user_id
    ) t1
    GROUP BY date
    ORDER BY date
) first_create_orders_users
using(date)
JOIN
(
    SELECT
        date,
        count(order_id) new_users_orders
    FROM
    (
        SELECT user_id,
        order_id,
        date_trunc('day', time) date
        FROM   user_actions
        WHERE  order_id not in (SELECT order_id
                                FROM   user_actions
                                WHERE  "action" like 'can%')) t1
        RIGHT JOIN
        (
            SELECT user_id,
                date_trunc('day', min(time)) date
            FROM   user_actions
            GROUP BY user_id
            ORDER BY user_id
        ) t2
        using(user_id, date)
        GROUP BY date
        ORDER BY date
) new_users_create_orders_day using(date)
        """)
        df_orders_users = data(format_cursor(cursor_1))

# print(df_orders_users.dtypes)


# ## Показатели, связанных с заказами

# In[47]:


fig = px.line(df_orders_users,
             x='date',
             y='orders',
             title='Динамика общего числа заказов / числа первых заказов / числа заказов новых пользователей',
             template='plotly_dark'
)

fig.update_traces(
    line_color=px.colors.qualitative.Set3[3],
    showlegend=True,
    name='orders'
)

fig1 = px.line(
    df_orders_users,
    x='date',
    y='first_orders'
)

fig1.update_traces(
    line_color=px.colors.qualitative.Set3[5],
    showlegend=True,
    name='first_orders'
)

fig.add_trace(fig1.data[0])


fig1 = px.line(
    df_orders_users,
    x='date',
    y='new_users_orders'
)

fig1.update_traces(
    line_color=px.colors.qualitative.Set3[6],
    showlegend=True,
    name='new_users_orders'
)

fig.add_trace(fig1.data[0])

fig.update_layout(barmode='group',
                  showlegend=True,
                  legend_title='Legend'
)

fig.update_yaxes(title_text='')
fig.update_xaxes(title_text='')

Order_related_indicators = fig


# In[48]:


fig = px.line(df_orders_users,
             x='date',
             y='first_orders_share',
             title='Динамика платящей доли пользователей / активной доли курьеров',
             template='plotly_dark'
)

fig.update_traces(
    line_color=px.colors.qualitative.Set3[3],
    showlegend=True,
    name='first_orders_share'
)

fig1 = px.line(
    df_orders_users,
    x='date',
    y='new_users_orders_share'
)

fig1.update_traces(
    line_color=px.colors.qualitative.Set3[5],
    showlegend=True,
    name='new_users_orders_share'
)

fig.add_trace(fig1.data[0])

fig.update_layout(barmode='group',
                  showlegend=True,
                  legend_title='Legend'
)

fig.update_yaxes(rangemode='tozero', title_text='')
fig.update_xaxes(title_text='')

Dynamics_of_users_and_couriers_share = fig


# ## Динамика числа пользователей и заказов на одного курьера

# In[49]:


with connect(**config) as connect_1:
    with connect_1.cursor() as cursor_1:
        cursor_1.execute("""
SELECT date::DATE,
       round(users_payed / courier_delivered::decimal, 2)::FLOAT users_per_courier,
       round(all_orders / courier_delivered::decimal, 2)::FLOAT orders_per_courier
FROM
(
    SELECT
        count(distinct user_id) users_payed,
        date_trunc('day', time) date
    FROM user_actions
    WHERE order_id not in (
        SELECT order_id
        FROM user_actions
        WHERE  "action" like 'can%')
    GROUP BY date
) users_payed
LEFT JOIN
(
    SELECT
        count(distinct courier_id) courier_delivered,
        date_trunc('day', time) date
    FROM courier_actions
    WHERE order_id in (
        SELECT order_id
        FROM   courier_actions
        WHERE  "action" like 'del%')
    GROUP BY date
) courier_delivered
using (date)
LEFT JOIN
(
    SELECT
        count(distinct order_id) all_orders,
        date_trunc('day', creation_time) date
    FROM orders
    WHERE order_id in (
        SELECT order_id
        FROM courier_actions
        WHERE "action" like 'del%')
    and order_id not in (
        SELECT order_id
        FROM user_actions
        WHERE "action" like 'can%')
    GROUP BY date
) filtered_orders_use_couriers_and_users
using (date)
        """)
        df_orders_users_per_courier = data(format_cursor(cursor_1))

# print(df_orders_users_per_courier.dtypes)


# In[50]:


fig = px.line(df_orders_users_per_courier,
             x='date',
             y='users_per_courier',
             title='Динамика числа пользователей и заказов на одного курьера',
             template='plotly_dark'
)

fig.update_traces(
    line_color=px.colors.qualitative.Set3[3],
    showlegend=True,
    name='users_per_courier'
)

fig1 = px.line(
    df_orders_users_per_courier,
    x='date',
    y='orders_per_courier'
)

fig1.update_traces(
    line_color=px.colors.qualitative.Set3[5],
    showlegend=True,
    name='orders_per_courier'
)

fig.add_trace(fig1.data[0])

fig.update_layout(barmode='group',
                  showlegend=True,
                  legend_title='Legend'
)

fig.update_yaxes(title_text='')
fig.update_xaxes(title_text='')

orders_users_per_courier = fig


# In[51]:


with connect(**config) as connect_1:
    with connect_1.cursor() as cursor_1:
        cursor_1.execute("""
SELECT date::DATE,
CASE
    WHEN EXTRACT(SECOND FROM AVG(time_deliver)) > 29 THEN EXTRACT(MINUTE FROM AVG(time_deliver))::INTEGER + 1
    ELSE EXTRACT(MINUTE FROM AVG(time_deliver))::INTEGER
END minutes_to_deliver
FROM
(
    SELECT
        order_id,
        deliver_order - accept_order time_deliver,
        date_trunc('day', accept_order) date
    FROM
    (
        SELECT
            order_id,
            min(time) accept_order,
            max(time) deliver_order
        FROM courier_actions
        WHERE order_id IN (
            SELECT order_id FROM courier_actions
            WHERE "action" LIKE 'del%'
        )
        GROUP BY order_id
    ) time_couriers
) time_deliver
GROUP BY date
ORDER BY date
        """)
        df_minutes_to_deliver = data(format_cursor(cursor_1))

# print(df_minutes_to_deliver.dtypes)


# In[52]:


fig = px.line(df_minutes_to_deliver,
             x='date',
             y='minutes_to_deliver',
             title='Динамика среднего времени доставки заказов',
             template='plotly_dark',
             markers=True
)

fig.update_traces(
    line_color=px.colors.qualitative.Set3[3],
    showlegend=True,
    name='minutes_to_deliver'
)

fig.update_yaxes(rangemode='tozero', title_text='')
fig.update_xaxes(title_text='')

average_delivery_time = fig


# ## Динамика показателя cancel rate и числа успешных/отменённых заказов

# In[53]:


with connect(**config) as connect_1:
    with connect_1.cursor() as cursor_1:
        cursor_1.execute("""
SELECT
    successful_orders,
    canceled_orders,
    ROUND(canceled_orders::DECIMAL / all_orders, 3)::FLOAT cancel_rate,
    hour
FROM
(
    SELECT
        COUNT(order_id) FILTER (
            WHERE order_id IN (
                SELECT DISTINCT order_id FROM courier_actions
                WHERE "action" LIKE 'del%'
            )
        ) successful_orders,
        COUNT(order_id) FILTER (
            WHERE order_id IN (
                SELECT DISTINCT order_id FROM user_actions
                WHERE "action" LIKE 'can%'
            )
        ) canceled_orders,
        COUNT(order_id) all_orders,
        EXTRACT(HOUR FROM creation_time)::INTEGER AS hour
    FROM orders
    GROUP BY hour
) result
ORDER BY hour
        """)
        df_Indicator_dynamics_orders = data(format_cursor(cursor_1))

# print(df_Indicator_dynamics_orders.dtypes)


# In[54]:


import plotly.graph_objects as go

fig = px.bar(
    df_Indicator_dynamics_orders,
    x='hour',
    y=['successful_orders', 'canceled_orders'],
    color_discrete_sequence=[px.colors.qualitative.Antique[4],
                              px.colors.qualitative.Antique[5]],
    title='Индикаторы динамики заказов'
)

fig.add_trace(
    go.Scatter(x=df_Indicator_dynamics_orders['hour'],
               y=df_Indicator_dynamics_orders['cancel_rate'],
               mode='lines+markers',
               marker_color=px.colors.qualitative.Set2[1],
               name='cancel_rate',
               yaxis='y2'
    )
)

fig.update_layout(template='plotly_dark',
                  barmode='relative',
                  showlegend=True,
                  legend_title='Indicator_dynamics_orders',
                  xaxis_title='Hour',
                  yaxis={'title': 'value (cancel_rate(%))', 'side': 'left'},
                  yaxis2={'overlaying': 'y', 'showticklabels': False})

Indicator_dynamics_orders = fig



# ## СОЗДАНИЕ ДАШБОРДА, столбцы:
#
#     Total_peoples
#     New_peoples
#     New_Peoples_Change
#     Total_peoples_growth
#     Active_peoples
#     Peoples_share
#     New_Peoples_Share
#     Order_related_indicators
#     Dynamics_of_users_and_couriers_share
#     orders_users_per_courier
#     average_delivery_time
#     Indicator_dynamics_orders
