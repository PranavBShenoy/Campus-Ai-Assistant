import { NextRequest, NextResponse } from 'next/server'

const publicRoutes = new Set(['/login', '/register'])

export function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname
  const hasToken = Boolean(request.cookies.get('access_token')?.value)
  if (!hasToken && !publicRoutes.has(path)) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  if (hasToken && publicRoutes.has(path)) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }
  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
