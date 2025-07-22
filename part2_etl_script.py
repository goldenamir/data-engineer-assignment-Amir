import pandas as pd
import numpy as np
import pytz


def load_data(path):
    return pd.read_parquet(path)


def explode_energy_arrays(df, timezone='Europe/Stockholm'):
    tz = pytz.timezone(timezone)
    records = []
    for _, row in df.iterrows():
        date = pd.to_datetime(row['date'])
        for hour, val in enumerate(row['energy_consumption']):
            ts = tz.localize(date.replace(
                hour=hour, minute=0, second=0, microsecond=0))
            records.append({
                'client_id': row['client_id'],
                'ext_dev_ref': row['ext_dev_ref'],
                'date': date.date(),
                'hour': hour,
                'energy_consumption': float(val),
                'resolution': row['resolution'],
                'timestamp': ts,
                'year': date.year,
                'month': date.month,
                'day': date.day,
                'day_of_week': date.dayofweek,
                'is_weekend': date.dayofweek >= 5
            })
    return pd.DataFrame(records)


def add_features(df):
    df = df.sort_values(['client_id', 'ext_dev_ref',
                        'timestamp']).reset_index(drop=True)
    df['energy_consumption_24h_avg'] = df.groupby(['client_id', 'ext_dev_ref'])['energy_consumption']\
        .transform(lambda x: x.rolling(window=24, min_periods=1).mean())
    df['energy_consumption_7d_avg'] = df.groupby(['client_id', 'ext_dev_ref'])['energy_consumption']\
        .transform(lambda x: x.rolling(window=24*7, min_periods=1).mean())
    df['hour_of_day_avg'] = df.groupby(['client_id', 'ext_dev_ref', 'hour'])[
        'energy_consumption'].transform('mean')
    df['day_of_week_avg'] = df.groupby(['client_id', 'ext_dev_ref', 'day_of_week'])[
        'energy_consumption'].transform('mean')
    df['consumption_category'] = pd.cut(
        df['energy_consumption'],
        bins=[0, 50, 100, 150, 200, float('inf')],
        labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
    )
    df['is_peak_hour'] = df['hour'].between(6, 22)
    df['season'] = pd.cut(
        df['month'],
        bins=[0, 3, 6, 9, 12],
        labels=['Winter', 'Spring', 'Summer', 'Fall']
    )
    return df


def save_data(df, path):
    df.to_parquet(path, index=False)


def main():
    input_path = 'data/home_assignment_raw_data.parquet'
    output_path = 'output/transformed_energy_data.parquet'
    df = load_data(input_path)
    df = explode_energy_arrays(df)
    df = add_features(df)
    save_data(df, output_path)
    print("ETL complete. Output saved to:", output_path)
    print(df.head())


if __name__ == "__main__":
    main()
