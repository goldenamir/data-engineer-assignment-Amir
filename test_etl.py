import sys
import os
import pandas as pd
from part2_etl_script import load_data, explode_energy_arrays, add_features, save_data


def test_etl_pipeline():

    input_path = 'data/home_assignment_raw_data.parquet'
    output_path = 'output/transformed_energy_data.parquet'

    print("Testing ETL Pipeline")
    print("=" * 50)

    try:
        df = load_data(input_path)
        print(f"Loaded {len(df)} daily records")
        df = explode_energy_arrays(df, timezone='Europe/Stockholm')
        print(f"Exploded to {len(df)} hourly records")
        df = add_features(df)
        save_data(df, output_path)
        print(f"Saved transformed data to {output_path}")

        
        transformed_df = pd.read_parquet(output_path)
        print(f"\n Sample of Transformed Data:")
        print(transformed_df.head(10).to_string(index=False))

        print(f"\n ETL pipeline test completed successfully!")
        print(f"   Output saved to: {output_path}")

    except Exception as e:
        print(f" ETL pipeline test failed: {e}")
        return False

    return True


if __name__ == "__main__":
    success = test_etl_pipeline()
    sys.exit(0 if success else 1)
