import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xlsxwriter as xl

def read_dataset():

    dataset = {
        #"money": [629.5, 578.25, 582.75, 568, 557, 535.5, 519.25, 521.5, 527, 518.25, 550.25, 507.25, 563.5, 522, 523, 532.25, 570, 591, 577.5, 612.5, 637.25, 623]
        #"money": [29.5, 25.7, 30.1, 22, 36.6, 37.2, 25.5, 30.9, 34.3, 25.5, 33.5, 32.8, 39.7, 31.3, 31.1, 32.4, 33.1, 31.6, 37.6, 28.8, 43.2, 39.5, 37.5, 43.2, 56, 42.7, 38.9, 41.3, 36.2, 32.7, 28.1, 33.6, 29.02, 37.84, 39, 44.4, 47.5, 33.8, 43.4, 46.8, 42.9, 45.4, 55.4, 46.1, 50.2, 55.3, 39.8, 50.1, 54.7, 57.5, 58.4, 62, 61.6, 59.7, 47.8, 60]
        "money": [
    2.1, 
    3.2, 
    2.5, 
    6.2, 
    5.2, 
    2.5, 
    2.4, 
    9, 
    4.4, 
    2.9, 
    4.8, 
    9.2, 
    8.4, 
    3.5, 
    7, 
    1.9, 
    0.9, 
    3.1, 
    6.2, 
    3.9, 
    2.8, 
    7, 
    12.7, 
    13, 
    5.8, 
    7.5, 
    3.9, 
    1.6, 
    6.1, 
    6.9, 
    5.1, 
    5, 
    6.9, 
    6.7, 
    5.6, 
    6.5, 
    5.1, 
    5.3, 
    2.9, 
    6.5, 
    6.2, 
    4, 
    6.4, 
    8.4, 
    5.2, 
    8.4, 
    6.3, 
    7.7, 
    7.2, 
    3.5, 
    3, 
    1, 
    7.9, 
    4.8, 
    1, 
    7.4, 
    6.7, 
    2.8, 
    2.7, 
    6.2, 
    9, 
    6.8, 
    8.3, 
    6.6, 
    9.5, 
    8.5, 
    8.2, 
    13.2, 
    13.1, 
    11.8, 
    10.2, 
    14, 
    12.5, 
    3.8, 
    7.7, 
    5.2, 
    5.5, 
    3, 
    9.1, 
    11.3, 
    8.6, 
    12, 
    17.4, 
    9.9, 
    11.5, 
    7.9, 
    13.6, 
    10.5, 
    15.1, 
    10.6, 
    17.7, 
    10.4, 
    18.1, 
    17.6, 
    8.1, 
    11.3, 
    18, 
    14, 
    16.5, 
    10.1, 
    20.9, 
    22.8, 
    13.9, 
    22.5, 
    15.8, 
    11, 
    13.6, 
    21.7, 
    27.2, 
    12.1, 
    23, 
    27.4, 
    20.4, 
    21.1, 
    21.6, 
    13.7, 
    27.3, 
    21.2, 
    27.6, 
    31, 
    35.2, 
    31.8, 
    29.7, 
    32.6, 
    25.3, 
    24.6, 
    21, 
    22.5, 
    22.11, 
    21.79, 
    22.6, 
    28.6, 
    33.1, 
    24, 
    34.9, 
    36.9, 
    33.3, 
    35.8, 
    38.6, 
    32.3, 
    33.7, 
    38.7, 
    21.9, 
    30.6, 
    39.2, 
    39.5, 
    42.8, 
    43.7, 
    39.6, 
    34.7, 
    26.3, 
    37.4]
    }
    return dataset

def get_writer():
    writer = pd.ExcelWriter("pa.xlsx", engine="xlsxwriter")
    return writer

def get_raw_phases(phases):
    raw_phases = phases.groupby(level=0).agg(["mean", "size"])
    return raw_phases

def write_iterations(phases, startcol, writer):
    raw_phases = get_raw_phases(phases)
    raw_phases["start"] = raw_phases["size"].cumsum() - raw_phases["size"] + 2
    worksheet =  writer.sheets['Исходный ряд']
    worksheet.write(0, startcol, phases.name)
    workbook = writer.book
    up = workbook.add_format({'fg_color': '#D7E4BC'})
    down = workbook.add_format({'fg_color': '#FA8072'})

    for row in raw_phases.iterrows():
        row = row[1]
        if row["mean"] > 0: format = up 
        else: format = down
        if row["size"] > 1:
            worksheet.merge_range(np.int32(row["start"]), startcol, np.int32(row["start"]+row["size"]-1), startcol, row["mean"], cell_format=format)
        else:
            worksheet.write(np.int32(row["start"]), startcol, row["mean"], format)


def write_charts(iterations, writer):
    workbook = writer.book
    chart = workbook.add_chart({'type': 'line'})
    for idx, i in enumerate(iterations):
        i.to_excel(writer, sheet_name='Графики', startcol=idx*2)
        chart.add_series({
            'values': ["Графики", 1, idx*2+1, 1+i.size, idx*2+1],
            'name': ["Графики", 0, idx*2+1],
            })
    else:
        chart.set_size({"x_scale": 2, "y_scale": 2})
        writer.sheets["Графики"].insert_chart(1, (idx+1)*2, chart)
    

def prepare_dataset(dataset, writer):
    s = pd.DataFrame(dataset)
    s["step"] = s["money"].pct_change()
    s.to_excel(writer, sheet_name="Исходный ряд")
    return s


def make_phases(s):
    groups = []

    while not s.empty:
        for window in s.expanding(min_periods=1):
            if window["money"].is_monotonic_increasing or window["money"].is_monotonic_decreasing:
                continue
            groups.append(window.iloc[1:-1])
            s = s.loc[window.index[-2]:]
            break
        else:
            groups.append(s.iloc[1:])
            break
    df = pd.concat(groups, keys=np.arange(len(groups)))

    gb = df.groupby(level=0)
    phases = gb["step"].transform("sum")
    phases.name = "Исходные фазы"
    return phases

def count_stats(phases, iteration):
    raw_phases = get_raw_phases(phases)
    raw_phases["sign"] = raw_phases.apply(lambda x: '+' if x["mean"] > 0 else '-', axis=1)
    gb_sign = raw_phases.groupby("sign")
    result = gb_sign.mean()
    result["len"] = gb_sign.size()
    result = result.T.stack()
    result.name = f"{iteration}"
    return result.to_frame()

def split_by_floor(phases, floor):
    sum_steps = get_raw_phases(phases)
    under_floor = sum_steps["mean"].apply(lambda x: abs(x) < floor)
    groups = []
    cur = 0

    while cur < sum_steps["mean"].size:
        if cur + 1 < under_floor.size and under_floor.loc[cur+1]:
            l, r = 0, 2
        elif under_floor.iloc[cur]:
            l, r = 0, 1
        else:
            l, r = 0, 0
        
        cum_phase = phases.loc[cur+l:cur+r]
        s = cum_phase.groupby(level=0).mean().sum()
        cum_phase[:] = s
        groups.append(cum_phase.droplevel(0))
        cur += r + 1

    new_phases = pd.concat(groups, keys=np.arange(len(groups)))
    return new_phases

def write_iteration_stats(iteration_stats, startcol, writer):
    iteration_stats = iteration_stats.rename({"mean": "Средняя мощность", "size": "Средняя продолжительность", "len": "Количество"})
    iteration_stats = iteration_stats.rename(columns=lambda x: f"Итерация {x}")
    iteration_stats.index.names = ("Показатель", "Знак")
    iteration_stats.to_excel(writer, sheet_name='Статистика', startcol=startcol)


def make_iteration(phases, iteration_num, floor, charts_phases, writer):
    phases = split_by_floor(phases, floor)
    phases.name = f"Итерация {iteration_num}"
    charts_phases.append(phases.droplevel(0))
    iteration_stats = count_stats(phases, iteration_num)
    write_iterations(phases, iteration_num+3, writer)
    write_iteration_stats(iteration_stats, (iteration_num)*3, writer)
    return phases


def main():
    writer = get_writer()
    dataset = read_dataset()
    s = prepare_dataset(dataset, writer)
    phases = make_phases(s)
    write_iterations(phases, 3, writer)
    iteration_stats = count_stats(phases, 0)
    print(iteration_stats)
    write_iteration_stats(iteration_stats, 0, writer)
    charts_phases = [phases.droplevel(0)]
    phases = make_iteration(phases, 1, 0.5, charts_phases, writer)
    phases = make_iteration(phases, 2, 0.8, charts_phases, writer)
    phases = make_iteration(phases, 3, 1., charts_phases, writer)
    write_charts(charts_phases, writer)
    for sheet in writer.sheets.values():
        sheet.autofit()
    writer.close()

main()