@echo off
echo ============================================
echo AnaTEMa Toolkit Installer
echo ============================================

echo Installing required Python packages...
pip install scipy numpy matplotlib requests beautifulsoup4 scikit-learn mplcursors plotly pandas openpyxl
pushd "./quadstarfiles-src"
pip install .
popd

echo.
echo Installation complete!
echo You can now run AnaTEMa with: python main.py
pause
