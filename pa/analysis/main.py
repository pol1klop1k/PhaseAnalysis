import pandas as pd
import numpy as np
import xlsxwriter as xl
from io import BytesIO

def read_dataset(file):
    f = BytesIO(file.read())
    dataset = pd.read_excel(f, index_col=0)
    return dataset

def get_writer(stream):
    writer = pd.ExcelWriter(stream, engine="xlsxwriter", engine_kwargs={'options': {'in_memory': True}})
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
    s["Прирост"] = s.iloc[:, 0].pct_change()
    s.to_excel(writer, sheet_name="Исходный ряд")
    s = s.rename(columns = {s.columns[0]: "value", "Прирост": "step"})
    return s


def make_phases(s):
    groups = []

    while not s.empty:
        for window in s.expanding(min_periods=1):
            if window["value"].is_monotonic_increasing or window["value"].is_monotonic_decreasing:
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
    return process("data.xlsx")

def process(file):
    stream = BytesIO()
    writer = get_writer(stream)
    dataset = read_dataset(file)
    s = prepare_dataset(dataset, writer)
    phases = make_phases(s)
    write_iterations(phases, 3, writer)
    iteration_stats = count_stats(phases, 0)
    write_iteration_stats(iteration_stats, 0, writer)
    charts_phases = [phases.droplevel(0)]
    phases = make_iteration(phases, 1, 0.5, charts_phases, writer)
    phases = make_iteration(phases, 2, 0.8, charts_phases, writer)
    phases = make_iteration(phases, 3, 1., charts_phases, writer)
    write_charts(charts_phases, writer)
    for sheet in writer.sheets.values():
        sheet.autofit()
    writer.close()
    return stream.getvalue()

if __name__ == "__main__":
    main()