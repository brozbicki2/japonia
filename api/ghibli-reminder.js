export default async function handler(req, res) {
  // Zabezpieczenie — tylko Vercel Cron może wywołać ten endpoint
  const authHeader = req.headers['authorization'];
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  const today = new Date();
  const reminderDate = new Date('2026-05-07');

  const isReminderDay =
    today.getUTCFullYear() === reminderDate.getUTCFullYear() &&
    today.getUTCMonth()    === reminderDate.getUTCMonth()    &&
    today.getUTCDate()     === reminderDate.getUTCDate();

  const isTestMode = req.query.test === 'true';

  if (!isReminderDay && !isTestMode) {
    return res.status(200).json({
      message: 'Nie czas jeszcze.',
      today: today.toISOString().split('T')[0],
      reminderDate: '2026-05-07',
    });
  }

  // Wyślij email przez Resend
  const response = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from: 'Ghibli Bilety 2026 <noreply@brozbicki.com>',
      to: ['bart.rozbicki@gmail.com', 'irena.gruca@gmail.com'],
      subject: isTestMode ? '[TEST] 🎬 ZA 3 DNI — Bilety do Muzeum Ghibli! Nastaw alarm na 2:50 w nocy' : '🎬 ZA 3 DNI — Bilety do Muzeum Ghibli! Nastaw alarm na 2:50 w nocy',
      html: `
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 24px;">
          <h1 style="color: #1a1a2e;">🎬 Muzeum Ghibli — Alarm!</h1>
          <div style="background: #fff3cd; border-left: 4px solid #f0a500; padding: 16px; border-radius: 8px; margin: 20px 0;">
            <strong>Za 3 dni — 10 maja 2026 — sprzedaż biletów!</strong>
          </div>
          <p style="font-size: 1.1rem; line-height: 1.7;">
            Bilety do Muzeum Ghibli w Mitace wychodzą <strong>10 maja 2026 o godz. 3:00 w nocy (czasu polskiego)</strong>.<br>
            Sprzedają się w ciągu kilku minut — <strong>nastaw alarm na 2:50</strong>!
          </p>
          <h2>Co zrobić:</h2>
          <ol style="line-height: 2;">
            <li>Nastaw alarm na <strong>2:50 w nocy, 10 maja 2026</strong></li>
            <li>Wejdź na <a href="https://l-tike.com/ghibli-museum/">Lawson Ticket</a> — upewnij się że masz konto!</li>
            <li>O 3:00 dokładnie — kup bilety na <strong>piątek, 5 czerwca 2026, godz. 10:00</strong></li>
            <li>Zarezerwuj dla 3 osób: Nina, Bartek, Irena</li>
          </ol>
          <div style="background: #c0392b; color: white; padding: 16px; border-radius: 8px; margin: 20px 0;">
            <strong>⚠️ Uwaga:</strong> Konto na Lawson Ticket musisz mieć założone WCZEŚNIEJ.<br>
            Nie czekaj z rejestracją do ostatniej chwili!
          </div>
          <a href="https://l-tike.com/ghibli-museum/"
             style="display:inline-block; background:#1a1a2e; color:white; padding:12px 24px; border-radius:8px; text-decoration:none; font-weight:bold;">
            → Lawson Ticket — Ghibli Museum
          </a>
          <p style="margin-top: 24px; color: #888; font-size: 0.85rem;">
            Plan podróży: <a href="https://japonia.vercel.app">japonia.vercel.app</a>
          </p>
          <img src="https://japonia.vercel.app/ghibli-studio.jpg"
               alt="Studio Ghibli"
               style="width: 100%; max-width: 600px; border-radius: 8px; margin-top: 24px; display: block;" />
        </div>
      `,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    return res.status(500).json({ error: 'Błąd wysyłki emaila', details: error });
  }

  return res.status(200).json({ message: 'Email wysłany! 📨' });
}
