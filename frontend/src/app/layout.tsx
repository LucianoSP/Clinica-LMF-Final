import './globals.css'
import { outfit } from '@/lib/fonts'
// import { Toaster } from '@/components/ui/toaster'
import { Toaster as SonnerToaster } from 'sonner'
import { Providers } from '@/app/providers'
import { metadata } from '@/app/metadata'

export { metadata }

interface RootLayoutProps {
  children: React.ReactNode
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body className={`min-h-screen bg-background ${outfit.className}`}>
        <Providers>
          <div className="contents">
            {children}
          </div>
          {/* <Toaster /> */}
          <SonnerToaster 
            position="top-center" 
            richColors
            closeButton
          />
        </Providers>
      </body>
    </html>
  )
}
