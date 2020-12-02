cd\Users\Dema
SET root=C:\Users\Dema\Anaconda3
CALL %root%\Scripts\activate.bat
CALL conda activate rl_fx
cd Documents/Programming/Python/GitHub/st-backtester
CALL python data_collector.py
CALL python data_processor.py