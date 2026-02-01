# Start Backend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {cd 'voxmark-backend'; python main.py}"

# Wait a moment for backend to init
Start-Sleep -Seconds 2

# Start Frontend (Tauri/Vite)
cd voxmark-frontend
npm run tauri dev
