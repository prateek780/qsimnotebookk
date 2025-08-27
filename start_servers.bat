@echo off
echo 🎯 Starting Quantum Network Simulation Servers
echo ================================================

echo 🚀 Starting backend server...
start "Backend Server" cmd /k "cd quantum_network && python main.py"

echo 🚀 Starting frontend server...
start "Frontend Server" cmd /k "cd ui && npm run dev"

echo ✅ Both servers are starting in separate windows
echo 🌐 Frontend will be available at: http://localhost:5173
echo 🔧 Backend will be available at: http://localhost:5174
echo 💡 Close the command windows to stop the servers
pause
