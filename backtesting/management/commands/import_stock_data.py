import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
import logging
from backtesting.models import StockData
from django.db import transaction


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import stock data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        full_file_path = os.path.join(settings.BASE_DIR, file_path)

        logger.info(f"Starting stock data import from {full_file_path}")

        try:
           
            df = pd.read_csv(full_file_path)
        except FileNotFoundError:
             logger.error(f"Error: File not found at path: {full_file_path}", exc_info=True)
             return
        except pd.errors.EmptyDataError:
             logger.error(f"Error: File is empty: {full_file_path}", exc_info=True)
             return
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}", exc_info=True)
            return

        df.columns = df.columns.str.strip().str.lower()  # Standardize column names

        # Ensure required columns exist
        required_columns = {'ticker', 'timestamp', 'open', 'high', 'low', 'close', 'volume'}
        if not required_columns.issubset(df.columns):
            logger.error(f"Error: Missing required columns: {required_columns - set(df.columns)}. Ensure the CSV contains {required_columns}", exc_info=True)
            return
        
        #Handle optional vwap column
        if 'vwap' not in df.columns:
            df['vwap'] = None # Create vwap column with null values if it doesn't exist
        

        # Convert timestamp
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='raise') #Raise error on invalid timestamp

        except Exception as e:
            logger.error(f"Error converting timestamps: {e}. Please ensure timestamps are in correct format", exc_info=True)
            return
        # Convert volume to integer and drop rows with invalid volumes
        try:
            df['volume'] = pd.to_numeric(df['volume'], errors='raise').astype('Int64')
            
            df=df.dropna(subset=['volume'])
        except Exception as e:
            logger.error(f"Error converting volume: {e}. Ensure the Volume Column contains numeric data.", exc_info=True)
            return



        # Bulk create using a transaction for atomicity
        with transaction.atomic():
            stock_data_instances = []
            for _, row in df.iterrows():
                try:
                    stock_data_instances.append(
                        StockData(
                            ticker=row['ticker'],
                            timestamp=row['timestamp'],
                            open=row['open'],
                            high=row['high'],
                            low=row['low'],
                            close=row['close'],
                            volume=int(row['volume']),
                            vwap=row['vwap']
                        )
                    )
                except Exception as e:
                    logger.error(f"Error processing row: {row}, Error: {e}", exc_info=True)
                    continue  # Skip row that causes error

            StockData.objects.bulk_create(stock_data_instances, batch_size=1000, ignore_conflicts=True)
            self.stdout.write(f"Successfully imported {len(stock_data_instances)} rows.")