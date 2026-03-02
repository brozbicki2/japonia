export default function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { login, password } = req.body;

  if (login === 'japonia' && password === 'lecimy2026') {
    res.setHeader(
      'Set-Cookie',
      'japonia_auth=jp2026_ok; Path=/; HttpOnly; SameSite=Strict; Max-Age=604800'
    );
    return res.status(200).json({ ok: true });
  }

  return res.status(401).json({ ok: false });
}
