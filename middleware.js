export const config = {
  matcher: ['/', '/index.html'],
};

export default function middleware(request) {
  const cookie = request.cookies.get('japonia_auth');

  if (!cookie || cookie.value !== 'jp2026_ok') {
    return Response.redirect(new URL('/login.html', request.url));
  }
}
