#           --- sumilation of sending many api requests  ----
for ($i=1; $i -le 40; $i++) {

    Invoke-WebRequest `
      -Uri "http://localhost:8080/api/bookings/$i" `
      -UseBasicParsing

    if ($i % 10 -eq 0) {
        try {
            Invoke-WebRequest `
             -Uri "http://localhost:8080/api/bookings/fail" `
             -UseBasicParsing
        } catch {}
    }

    if ($i % 25 -eq 0) {
        Invoke-WebRequest `
         -Uri "http://localhost:8080/api/bookings/slow" `
         -UseBasicParsing
    }
}