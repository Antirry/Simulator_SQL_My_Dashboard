
# Дашборд по второй главе - первого урока курса
### [Симулятор SQL Глава 2 - Урок 1 - Метрики и графики](https://karpov.courses/simulator-sql)

Сначала я реализовал графики в аналоге tableau [pygwalker](https://github.com/Kanaries/pygwalker), для понимания в каком виде лучше их показать (Результат в папке OLD_VERSIONS).

Но я не мог их наложить друг на друга, поэтому я визуализировав данные через библиотеку [altair](https://altair-viz.github.io) (Результат в папке OLD_VERSIONS),

Поняв, что ее функционал устарел я использовал [plotly](https://plotly.com/python/) в двух версиях [graph_object](https://plotly.com/python/graph-objects/) и [express](https://plotly.com/python/plotly-express/),

Увидев, что графики в объектах не имеют точные названия (имен столбцов) данных при наведении курсором, я решил использовать *express* и в ***случае совмещения двух разных  графиков с разными осями*** использовал *graph-objects*

Конечная реализация с добавлением всех графиков на одну страницу была сделана с помощью [streamlit](https://github.com/streamlit/streamlit)

Код дашборда - [Dashboard EXPRESS ГЛАВА_2_1_Метрики_и_графики_ЗАДАНИЯ.py](LAST_VERISIONS\Dashboard EXPRESS ГЛАВА_2_1_Метрики_и_графики_ЗАДАНИЯ.py)

Код графиков - [EXPRESS_ГЛАВА_2_1_Метрики_и_графики_ЗАДАНИЯ.ipynb](LAST_VERISIONS\EXPRESS_ГЛАВА_2_1_Метрики_и_графики_ЗАДАНИЯ.ipynb)

Результат дашборда - [Dashboard_result.pdf](https://github.com/Antirry/Simulator_SQL_My_Dashboard/blob/master/LAST_VERISIONS/result_dashboard/Dashboard_result.pdf)