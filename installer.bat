@echo off
echo ============================================
echo AnaTEMa Toolkit Installer
echo ============================================

echo Installing required Python packages...
pip install scipy numpy matplotlib requests beautifulsoup4
pushd "./quadstarfiles"
pip install .
popd

echo.
echo Installation complete!
echo You can now run AnaTEMa with: python main2_0.py
pause
