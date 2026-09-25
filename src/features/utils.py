"""
Feature Engineering Utilities

Owner: Abhishek
Project: Customer Churn Prediction & LTV Engine
Purpose:
Provides performance profiling, memory optimization helpers, 
and execution timing utilities for the feature pipeline.
"""

import functools
import logging
import time
from typing import Callable, Any

import pandas as pd

logger = logging.getLogger(__name__)


def timeit(func: Callable) -> Callable:
    """Decorator to measure and log execution time of feature functions."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start_time
        logger.info("[TIMER] %s executed in %.3f seconds", func.__name__, duration)
        return result
    return wrapper


def reduce_mem_usage(df: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    """
    Iterate through numerical columns and downcast types to save memory.
    """
    numerics = ["int16", "int32", "int64", "float16", "float32", "float64"]
    start_mem = df.memory_usage().sum() / 1024**2
    df_opt = df.copy()

    for col in df_opt.columns:
        col_type = df_opt[col].dtypes
        if col_type in numerics:
            c_min = df_opt[col].min()
            c_max = df_opt[col].max()
            if str(col_type)[:3] == "int":
                if c_min > -128 and c_max < 127:
                    df_opt[col] = df_opt[col].astype("int8")
                elif c_min > -32768 and c_max < 32767:
                    df_opt[col] = df_opt[col].astype("int16")
                elif c_min > -2147483648 and c_max < 2147483647:
                    df_opt[col] = df_opt[col].astype("int32")
            else:
                if c_min > -65500 and c_max < 65500:
                    df_opt[col] = df_opt[col].astype("float32")

    end_mem = df_opt.memory_usage().sum() / 1024**2
    if verbose:
        logger.info("Memory usage reduced from %.2f MB to %.2f MB (%.1f%% reduction)",
                    start_mem, end_mem, 100 * (start_mem - end_mem) / start_mem)
    return df_opt
