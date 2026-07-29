for ($i=1; $i -le 20; $i++) { 
    Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:8090/api/bookings/$i" | Out-Null; 
    Start-Sleep -Seconds 2 
}; 
Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:8090/api/bookings/slow" | Out-Null; 
Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:8090/api/bookings/slow" | Out-Null; 
for ($i=1; $i -le 20; $i++) { 
    Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:8090/api/bookings/$i" | Out-Null; 
    Start-Sleep -Seconds 2 
} 