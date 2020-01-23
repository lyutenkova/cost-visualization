import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def get_data_from_xslx(file_path):
    ''' Получаем данные из файла в виде DataFrame'''
    df = pd.read_excel(file_path, names=['number', 'title', 'cost'])
    return df


def create_ds_for_drawing():
    ''' Собираем датасет удобный для построения диаграммы'''
    dataset = []
    df = get_data_from_xslx("./data.xlsx")
    
    for i in df.index:
        if not np.isnan(df['number'][i]):
            parent = str(df['title'][i])  #  родительская статья расходов
            continue
        
        if str(df['title'][i]) == 'ВСЕГО РАСХОДОВ с учетом процентов':  #  далее мы просто просуммируем все расходы, так что эта строка не нужна
            continue

        if str(df['title'][i]) == "ИТОГО РАСХОДОВ":  #  незначимая строка
            continue

        if 'Расшифровка затрат' in str(df['title'][i]):  #  незначимые строки
            continue

        if 'Физические лица' in str(df['title'][i]):  #  незначимые строки
            continue

        expenditure = str(df['title'][i])  # статья расходов потомок
        cost = int(float(df['cost'][i])) if not np.isnan(df['cost'][i]) else 0  #  сумма

        dataset.append([expenditure, parent, cost])
    
    return pd.DataFrame(dataset, columns = ['child', 'parent', 'cost'])


def draw_animate_chart():
    df = create_ds_for_drawing()  #  готовим датасет для рисования диаграммы
    levels = ['child', 'parent']  #  уровни вложенности (children, статья)
    value_column = 'cost'  #  по какому столбцу считать
    
    df_all_trees = pd.DataFrame(columns=['id', 'parent', 'value', 'color'])

    for i, level in enumerate(levels):
        df_tree = pd.DataFrame(columns=['id', 'parent', 'value', 'color'])  #  делаем дерево по иерархии
        dfg = df.groupby(levels[i:]).sum(numerical_only=True).round({'cost':2})  #  считаем суммы по уровням 
        dfg = dfg.reset_index()
        df_tree['id'] = dfg[level].copy()  #  добавляем ids (в дальнейшем лейблы)

        if i < len(levels) - 1:
            df_tree['parent'] = dfg[levels[i+1]].copy()  #  пока не дойдем до последнего уровня заносим в parent значения
        else:
            df_tree['parent'] = 'total'  #  на последнем уровне родителей нет, и сумма будет общая

        df_tree['value'] = dfg[value_column]
        df_all_trees = df_all_trees.append(df_tree, ignore_index=True)  # добавляем поддерево

    total = pd.Series(dict(id='total', parent='', 
                        value=df[value_column].sum().round(2)))  #  считаем общую сумму
    
    df_all_trees = df_all_trees.append(total, ignore_index=True)

    fig = make_subplots(1, 2, specs=[[{"type": "domain"}, {"type": "domain"}]],)

    #  подписи к секторам
    fig.add_trace(go.Sunburst(
        name="",
        labels=df_all_trees['id'],
        parents=df_all_trees['parent'],
        values=df_all_trees['value'],
        branchvalues='total',
        hovertemplate='<b>%{label} </b> <br> Cost: %{value}',
        ), 1, 1)

    fig.update_layout(
        title={"text":"Визуализация расходов на закрытие олимпиады в Сочи", "font":{"family": "'Open Sans', verdana, arial, sans-serif", "size": 22}},
        font={"family": "'Open Sans', verdana, arial, sans-serif"}        
    )

    fig.show()


if __name__ == "__main__":
    draw_animate_chart()