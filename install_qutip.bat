@echo off
echo Installing QuTiP and dependencies in virtual environment for Python 3.13.3
echo =================================================================

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Upgrading pip first...
python -m pip install --upgrade pip

echo Installing NumPy (required for QuTiP)...
python -m pip install "numpy>=1.24.0,<2.0"

echo Installing SciPy (required for QuTiP)...
python -m pip install "scipy>=1.10.0"

echo Installing matplotlib...
python -m pip install "matplotlib>=3.7.0"

echo Installing QuTiP compatible version...
python -m pip install "qutip==4.7.5"

echo Installing other quantum networking dependencies...
python -m pip install "ipywidgets>=8.1.0"
python -m pip install "requests>=2.31.0"
python -m pip install "seaborn>=0.12.0"

echo Testing QuTiP installation...
python -c "import qutip as qt; print('QuTiP version:', qt.__version__); print('QuTiP imported successfully!')"

echo Installation complete!
pause
